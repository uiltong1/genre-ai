import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Analyze from './Analyze';

const mockResult = {
  filename: 'musica.mp3',
  predicted_genre: 'rock',
  confidence: 0.9234,
  confidence_percentage: '92.34%',
  all_probabilities: {
    blues: 0.01,
    classical: 0.01,
    country: 0.01,
    disco: 0.01,
    hiphop: 0.01,
    jazz: 0.01,
    metal: 0.02,
    pop: 0.05,
    reggae: 0.01,
    rock: 0.86,
  },
};

function renderAnalyze() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<Analyze />} />
        <Route path="/result" element={<h1>Página de Resultado</h1>} />
      </Routes>
    </MemoryRouter>
  );
}

function createFile(name, type = 'audio/mpeg') {
  return new File(['fake-audio-content'], name, { type });
}

describe('Analyze', () => {
  test('renderiza o formulário de upload', () => {
    renderAnalyze();

    expect(
      screen.getByRole('heading', { name: 'Analisar Música' })
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Selecione uma música')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Analisar' })
    ).toBeInTheDocument();
    expect(screen.getByText(/Formatos:/)).toBeInTheDocument();
  });

  test('exibe erro ao enviar sem selecionar arquivo', async () => {
    renderAnalyze();

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(await screen.findByText('Selecione uma música!')).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('exibe erro para extensão não suportada', () => {
    renderAnalyze();

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, {
      target: { files: [createFile('documento.pdf', 'application/pdf')] },
    });

    expect(
      screen.getByText(/Formato não suportado: \.pdf/)
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Analisar' })).toBeEnabled();
  });

  test('aceita arquivo com extensão válida e faz upload para /predict', async () => {
    renderAnalyze();

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResult),
    });

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, { target: { files: [createFile('musica.mp3')] } });

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(await screen.findByText('Analisando...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Analisando...' })).toBeDisabled();

    expect(await screen.findByText('Página de Resultado')).toBeInTheDocument();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('/predict');
    expect(options.method).toBe('POST');
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.body.get('file')).toBeInstanceOf(File);
    expect(options.body.get('file').name).toBe('musica.mp3');
  });

  test('exibe erro quando a API retorna detalhes de validação', async () => {
    renderAnalyze();

    global.fetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: () =>
        Promise.resolve({
          detail: [
            {
              loc: ['body', 'file'],
              type: 'value_error',
              msg: 'Formato inválido',
            },
          ],
        }),
    });

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, { target: { files: [createFile('musica.mp3')] } });

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(
      await screen.findByText('[body.file] value_error: Formato inválido')
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Analisar' })
    ).toBeInTheDocument();
  });

  test('exibe mensagem de erro quando a API retorna detail string', async () => {
    renderAnalyze();

    global.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: 'Erro interno do servidor' }),
    });

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, { target: { files: [createFile('musica.mp3')] } });

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(
      await screen.findByText('Erro interno do servidor')
    ).toBeInTheDocument();
  });

  test('exibe status quando a resposta não tem corpo JSON', async () => {
    renderAnalyze();

    global.fetch.mockResolvedValue({
      ok: false,
      status: 502,
      json: () => Promise.reject(new Error('invalid json')),
    });

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, { target: { files: [createFile('musica.mp3')] } });

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(await screen.findByText('Erro 502')).toBeInTheDocument();
  });

  test('exibe erro de rede quando o fetch falha', async () => {
    renderAnalyze();

    global.fetch.mockRejectedValue(new Error('Failed to fetch'));

    const input = screen.getByLabelText('Selecione uma música');
    fireEvent.change(input, { target: { files: [createFile('musica.mp3')] } });

    fireEvent.click(screen.getByRole('button', { name: 'Analisar' }));

    expect(await screen.findByText('Failed to fetch')).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Analisar' })).toBeEnabled()
    );
  });
});
