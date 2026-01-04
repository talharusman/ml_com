import { useState, useEffect } from 'react';
import { fetchTemplate, fetchSampleData, getDownloadUrl } from '../api/client';

export default function TaskModal({ task, onClose, onSubmit }) {
  const [template, setTemplate] = useState('');
  const [sampleData, setSampleData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [templateData, dataRes] = await Promise.all([
          fetchTemplate(task.id),
          fetchSampleData(task.id).catch(() => null),
        ]);
        setTemplate(templateData.code);
        setSampleData(dataRes);
      } catch (err) {
        console.error('Error loading task data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [task.id]);

  const copyTemplateCode = () => {
    navigator.clipboard.writeText(template)
      .then(() => alert('Template code copied to clipboard!'))
      .catch(err => console.error('Failed to copy:', err));
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/85 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative z-10 w-full max-w-5xl max-h-[90vh] overflow-y-auto bg-bg-dark text-white rounded-xl p-8 mx-4">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-6 text-4xl hover:text-primary transition-colors"
        >
          ×
        </button>

        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold">{task.name} - Question {task.id}</h2>
          <p className="mt-3 text-gray-300">{task.description}</p>
          <p className="mt-2 font-semibold text-primary">
            {task.type === 'eda' ? `Score Method: ${task.metric}` : `Evaluation Metric: ${task.metric}`}
          </p>
        </div>

        {loading ? (
          <div className="text-center py-10">
            <div className="inline-block w-8 h-8 border-4 border-gray-400 border-t-primary rounded-full animate-spin"></div>
            <p className="mt-2 text-gray-400">Loading...</p>
          </div>
        ) : (
          <>
            {/* Template Code */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-primary mb-4">TEMPLATE CODE</h3>
              <pre className="bg-black/50 border-2 border-gray-700 rounded-lg p-4 text-green-400 font-mono text-sm overflow-x-auto whitespace-pre-wrap max-h-80">
                {template}
              </pre>
              <button
                onClick={copyTemplateCode}
                className="mt-3 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded font-semibold transition-colors"
              >
                COPY CODE
              </button>
            </div>

            {/* Sample Data */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-primary mb-4">SAMPLE DATA</h3>
              <div className="bg-black/50 border-2 border-gray-700 rounded-lg p-4 overflow-auto max-h-80">
                {sampleData && sampleData.data && sampleData.data.length > 0 ? (
                  <>
                    <p className="text-gray-400 mb-3">
                      Showing {sampleData.data.length} rows from dataset with {sampleData.shape[1]} columns
                    </p>
                    <table className="w-full text-sm">
                      <thead className="bg-secondary sticky top-0">
                        <tr>
                          {sampleData.columns.map((col, i) => (
                            <th key={i} className="px-3 py-2 text-left font-semibold">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {sampleData.data.slice(0, 10).map((row, i) => (
                          <tr key={i} className="border-b border-gray-700 hover:bg-gray-800">
                            {sampleData.columns.map((col, j) => (
                              <td key={j} className="px-3 py-2">
                                {row[col] === null ? 'null' : 
                                 typeof row[col] === 'number' ? row[col].toFixed(2) : row[col]}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                ) : (
                  <p className="text-gray-400">No data available</p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center pt-4 border-t border-gray-700">
              <a
                href={getDownloadUrl(task.id)}
                className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded font-semibold transition-colors"
              >
                DOWNLOAD DATA
              </a>
              <div className="flex gap-4">
                <button
                  onClick={onClose}
                  className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded font-semibold transition-colors"
                >
                  CLOSE
                </button>
                <button
                  onClick={() => onSubmit(task.id)}
                  className="px-6 py-2 bg-primary hover:bg-red-700 rounded font-semibold transition-colors"
                >
                  SUBMIT
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
