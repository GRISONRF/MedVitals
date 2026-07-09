/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { FHIRPatient, VitalObservation } from './types';

function App() {
  const [patients, setPatients] = useState<FHIRPatient[]>([]);
  const [selectedId, setSelectedId] = useState<string>('1');
  const [vitals, setVitals] = useState<VitalObservation[]>([]);

  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [exportStatus, setExportStatus] = useState<string>('idle'); // idle, processing, completed
  const [exportProgress, setExportProgress] = useState<number>(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  
  // Provider Form State
  const [npi, setNpi] = useState('');
  // const [docName, setDocName] = useState('');
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  // Fetch all patients on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/patients')
      .then(res => res.json())
      .then(data => setPatients(data))
      .catch(err => console.error("Error fetching patients", err));
  }, []);

  // Fetch vitals whenever the selected patient changes
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/patients/${selectedId}/vitals`)
      .then(res => res.json())
      .then(data => {
      console.log("Fetched vitals:", data)
      setVitals(data);
    })
      .catch(err => console.error("Error fetching vitals", err));
  }, [selectedId]);

  // Handle Medallion-style verification submission
  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setVerificationResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/providers/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ npi_number: npi})
        // body: JSON.stringify({ npi_number: npi, provider_name: docName })

      });
      const data = await response.json();
      console.log("Backend payload received:", data);
      console.log("Doctor Name:", data.provider_name);
      setVerificationResult(data);

    } catch (error) {
      console.error("Verification failed", error);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleBulkExport = async () => {
    setExportStatus('processing');
    setExportProgress(25);
    setDownloadUrl(null);

    try {
      // 1. Kick off the asynchronous process
      const response = await fetch('http://127.0.0.1:8000/api/patients/$export', {
        method: 'POST'
      });
      const initiationData = await response.json();
      const jobId = initiationData.job_id;
      setCurrentJobId(jobId);

      // 2. Start a polling clock that ticks every 2 seconds
      const pollingInterval = setInterval(async () => {
        const statusResponse = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}`);
        const jobData = await statusResponse.json();

        console.log("Polling background job state:", jobData);

        if (jobData.status === 'completed') {
          setExportStatus('completed');
          setExportProgress(100);
          setDownloadUrl(jobData.download_url);
          clearInterval(pollingInterval); // Stop ticking the clock!
        } else {
          // Boost up the mock loading meter steps while compiling
          setExportProgress(prev => (prev < 90 ? prev + 15 : prev));
        }
      }, 2000);

    } catch (error) {
      console.error("Bulk export execution failed", error);
      setExportStatus('idle');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="max-w-6xl mx-auto mb-8">
        <h1 className="text-3xl font-bold text-gray-900">MedVitals Provider Operations Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Full-Stack Python & React Architecture</p>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* LEFT COLUMN: FHIR CLINICAL DATA CONTAINER */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-emerald-700">Patient Clinical Tracker (HL7 FHIR Format)</h2>
          
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Active Patient Profile:</label>
          <select 
            className="w-full p-2 border border-gray-300 rounded-md mb-6 bg-white"
            value={selectedId} 
            onChange={(e) => setSelectedId(e.target.value)}
          >
            {patients.map(p => (
              <option key={p.id} value={p.id}>
                {p.name[0].given.join(' ')} {p.name[0].family} (ID: {p.id})
              </option>
            ))}
          </select>

          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">Live Vital Observations</h3>
          <div className="space-y-3">
            {vitals.map(v => (
              <div key={v.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                <span className="font-medium text-gray-700">{v.code.text}</span>
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold text-sm">{v.valueQuantity.value} {v.valueQuantity.unit}</span>
              </div>
            ))}
          </div>
        </section>

        {/* RIGHT COLUMN: MEDALLION COMPLIANCE ENGINE */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-blue-700">Provider Credentialing Engine</h2>
          <p className="text-xs text-gray-400 mb-4">Simulates background license validation API check</p>

          <form onSubmit={handleVerify} className="space-y-4">
            {/* <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider Full Name</label>
              <input 
                type="text" required value={docName} onChange={e => setDocName(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md" placeholder="Dr. Alice Smith"
              />
            </div> */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">National Provider Identifier (10-Digit NPI)</label>
              <input 
                type="text" required value={npi} onChange={e => setNpi(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md" placeholder="1234567890"
              />
            </div>
            <button 
              type="submit" disabled={isVerifying}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition disabled:bg-blue-300"
            >
              {isVerifying ? 'Querying State Boards...' : 'Verify Provider License'}
            </button>
          </form>

          {/* RESPONSE METRICS DISPLAY */}
          {verificationResult && (
            <div className={`mt-6 p-4 rounded-lg border ${verificationResult.verified ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'}`}>
              <h4 className="font-bold mb-1">Verification Status: {verificationResult.status.toUpperCase()}</h4>
              {verificationResult.verified ? (
                <div className="text-sm space-y-1">
                  {/* Match your new backend key: provider_name */}
                  <p><strong>Verified Clinician:</strong> {verificationResult.provider_name}</p>
                  <p><strong>License Hash:</strong> <code>{verificationResult.assigned_credentials}</code></p>
                  {/* NEW LINK COMPONENT */}
                  <p>
                    <strong>Registry Profile:</strong>{' '}
                    <a 
                      href={`https://npiregistry.cms.hhs.gov/provider-view/${npi}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline font-medium inline-flex items-center gap-1"
                    >
                      Clinician's Registry Link
                      <span className="text-xs">↗</span>
                    </a>
                  </p>
                </div>
              ) : (
                <p className="text-sm">Alert: {verificationResult.reason}</p>
              )}
            </div>
          )}
        </section>

        {/* FULL WIDTH LOWER SECTION: BULK DATA EXPORT PIPELINE */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 md:col-span-2 mt-4">
          <h2 className="text-xl font-semibold mb-2 text-purple-700">Enterprise FHIR Bulk Data Export Pipeline</h2>
          <p className="text-xs text-gray-500 mb-6">Simulates an asynchronous server thread compressing complete clinical registries into a single flat .ndjson bundle payload.</p>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-purple-50 rounded-lg border border-purple-100">
            <div>
              <h4 className="font-bold text-purple-900">Population Registry Data Extraction</h4>
              <p className="text-xs text-purple-700 mt-1">Status: <span className="uppercase font-extrabold">{exportStatus}</span> {currentJobId && `(Token: ${currentJobId.slice(0,8)}...)`}</p>
            </div>
            
            {exportStatus === 'idle' && (
              <button 
                onClick={handleBulkExport}
                className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-md transition shadow-sm text-sm"
              >
                Initialize population $export
              </button>
            )}

            {exportStatus === 'processing' && (
              <div className="w-full sm:w-64">
                <div className="flex justify-between text-xs text-purple-700 mb-1 font-medium">
                  <span>Compiling Flat FHIR stream...</span>
                  <span>{exportProgress}%</span>
                </div>
                <div className="w-full bg-purple-200 h-2 rounded-full overflow-hidden">
                  <div className="bg-purple-600 h-full transition-all duration-500" style={{ width: `${exportProgress}%` }}></div>
                </div>
              </div>
            )}

            {exportStatus === 'completed' && downloadUrl && (
              <div className="flex items-center gap-3">
                <a 
                  href={downloadUrl} target="_blank" rel="noopener noreferrer"
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-md transition shadow-sm text-sm inline-flex items-center gap-2"
                >
                  Download .ndjson Bundle ⬇
                </a>
                <button 
                  onClick={() => setExportStatus('idle')}
                  className="text-xs text-purple-600 hover:underline font-medium"
                >
                  Reset pipeline
                </button>
              </div>
            )}
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;