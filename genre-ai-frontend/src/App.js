import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Analyze from './pages/Analyze';
import Result from './pages/Result';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Analyze />} />
        <Route path="/result" element={<Result />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
