import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  test('renderiza a página de análise na rota inicial', () => {
    window.history.pushState({}, '', '/');
    render(<App />);

    expect(
      screen.getByRole('heading', { name: 'Analisar Música' })
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Selecione uma música')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Analisar' })
    ).toBeInTheDocument();
  });
});
