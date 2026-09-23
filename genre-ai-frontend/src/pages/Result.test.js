import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Result from './Result';

jest.mock('recharts', () => {
  const React = require('react');
  const Actual = jest.requireActual('recharts');
  return {
    ...Actual,
    ResponsiveContainer: ({ children }) => {
      const child = React.Children.only(children);
      return React.cloneElement(child, { width: 500, height: 400 });
    },
  };
});

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

function renderResult(state) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/result', state }]}>
      <Routes>
        <Route path="/result" element={<Result />} />
        <Route path="/" element={<h1>Página de Análise</h1>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('Result', () => {
  test('renderiza gênero, confiança e filename', () => {
    renderResult({ result: mockResult });

    expect(
      screen.getByRole('heading', { name: 'Resultado da Análise' })
    ).toBeInTheDocument();
    expect(screen.getByText('musica.mp3')).toBeInTheDocument();
    expect(
      screen.getByText('rock', { selector: 'span.text-4xl' })
    ).toBeInTheDocument();
    expect(screen.getByText('92.34%')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'Probabilidade por gênero' })
    ).toBeInTheDocument();
  });

  test('renderiza as barras de probabilidade de todos os gêneros', () => {
    renderResult({ result: mockResult });

    Object.keys(mockResult.all_probabilities).forEach((genre) => {
      const label = genre.charAt(0).toUpperCase() + genre.slice(1);
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    });
  });

  test('volta para a página de análise ao clicar em Voltar', () => {
    renderResult({ result: mockResult });

    fireEvent.click(screen.getByRole('button', { name: /Voltar/ }));

    expect(screen.getByText('Página de Análise')).toBeInTheDocument();
  });

  test('redireciona para a página inicial quando não há estado', async () => {
    renderResult(undefined);

    expect(await screen.findByText('Página de Análise')).toBeInTheDocument();
  });
});
