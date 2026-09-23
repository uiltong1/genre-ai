import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ALLOWED_EXTENSIONS = [
  '.mp3',
  '.wav',
  '.mp4',
  '.ogg',
  '.flac',
  '.m4a',
  '.aac',
  '.mkv',
];

function Analyze() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const parseError = (data, status) => {
    if (data && Array.isArray(data.detail)) {
      return data.detail.map((d) => {
        const loc = Array.isArray(d.loc) ? d.loc.join('.') : '';
        return `[${loc}] ${d.type}: ${d.msg}`;
      });
    }
    if (data && data.detail) {
      return [String(data.detail)];
    }
    return [`Erro ${status}`];
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) {
      setFile(null);
      return;
    }

    const ext = '.' + selected.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError([`Formato não suportado: ${ext}. Formatos aceitos: ${ALLOWED_EXTENSIONS.join(', ')}`]);
      setFile(null);
      e.target.value = '';
      return;
    }

    setError(null);
    setFile(selected);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError(['Selecione uma música!']);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/predict', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        setError(parseError(data, response.status));
        return;
      }

      navigate('/result', { state: { result: data } });
    } catch (err) {
      setError([err.message]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-gray-700">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-white tracking-tight">
            Genre <span className="text-indigo-400">AI</span>
          </h1>
          <p className="text-gray-400 text-sm mt-2">
            Classificador de gêneros musicais com inteligência artificial
          </p>
        </div>

        <h2 className="text-lg font-semibold text-white text-center mb-4">
          Analisar Música
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="file"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Selecione uma música
            </label>
            <input
              type="file"
              id="file"
              accept={ALLOWED_EXTENSIONS.join(',')}
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-indigo-600 file:text-white
                hover:file:bg-indigo-500
                cursor-pointer
                bg-gray-700 border border-gray-600
                rounded-lg p-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              Formatos: {ALLOWED_EXTENSIONS.join(', ')}
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500
              text-white font-bold py-3 px-4 rounded-lg
              transition duration-200 ease-in-out
              transform hover:scale-105
              focus:outline-none focus:ring-2 focus:ring-indigo-400
              disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? 'Analisando...' : 'Analisar'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-300 text-sm space-y-1">
            {error.map((msg, i) => (
              <p key={i}>{msg}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Analyze;
