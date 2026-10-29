
import { useState } from 'react'
import {
  LayoutDashboard, FileSearch, History, Settings,
  ShieldCheck, Upload, AlertTriangle, FileText,
  TrendingUp, CheckCircle, Menu, X
} from 'lucide-react'
import './App.css'

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard },
  { name: 'Invoice Analysis', icon: FileSearch },
  { name: 'Shop History', icon: History },
  { name: 'Settings', icon: Settings },
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [menuOpen, setMenuOpen] = useState(false)
  const [file, setFile] = useState(null)
  
const [invoiceData, setInvoiceData] = useState({
  invoice_id: 'INV-TEST-001',
  shop_id: 'SHOP001',
  quantity: '10',
  unit_price: '100',
  taxable_value: '1000',
  gst_rate: '18',
  gst_amount: '180',
  total_amount: '1180',
  invoice_age_days: '10',
})

const [result, setResult] = useState(null)
const [loading, setLoading] = useState(false)
const [apiError, setApiError] = useState('')


async function analyzeInvoice(event) {
  event.preventDefault()
  setLoading(true)
  setApiError('')
  setResult(null)

  try {
    const response = await fetch('http://127.0.0.1:8001/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...invoiceData,
        quantity: Number(invoiceData.quantity),
        unit_price: Number(invoiceData.unit_price),
        taxable_value: Number(invoiceData.taxable_value),
        gst_rate: Number(invoiceData.gst_rate),
        gst_amount: Number(invoiceData.gst_amount),
        total_amount: Number(invoiceData.total_amount),
        invoice_age_days: Number(invoiceData.invoice_age_days),
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail?.[0]?.msg || data.detail || 'Analysis failed')
    }

    setResult(data)
  } catch (error) {
    setApiError(error.message || 'Could not connect to the backend.')
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="app">
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={26} /></div>
          <div><h2>GSTGuard-I</h2><span>Invoice Intelligence</span></div>
          <button className="close-menu" onClick={() => setMenuOpen(false)}><X /></button>
        </div>

        <p className="nav-label">WORKSPACE</p>
        <nav>
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${activePage === name ? 'active' : ''}`}
              onClick={() => {
                setActivePage(name)
                setMenuOpen(false)
              }}
            >
              <Icon size={19} />
              <span>{name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <ShieldCheck size={22} />
          <p><strong>GSTGuard Protection</strong><br />
            <span>AI-assisted invoice review</span></p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)}><Menu /></button>
          <div><span className="breadcrumb">Workspace / </span>{activePage}</div>
          <div className="status"><span className="status-dot" /> Prototype</div>
        </header>

        <section className="content">
          <div className="welcome">
            <div>
              <p className="eyebrow">GST COMPLIANCE INTELLIGENCE</p>
              <h1>{activePage === 'Dashboard' ? 'Invoice Intelligence Dashboard' : activePage}</h1>
              <p className="subtitle">
                Detect unusual invoice patterns and review potential GST compliance risks.
              </p>
            </div>
            <div className="date-chip">GSTGuard-I · MVP</div>
          </div>

          {activePage === 'Dashboard' && (
            <>
              <div className="stats">
                <Stat icon={FileText} label="Invoices Analysed" value="0" note="No analyses yet" />
                <Stat icon={CheckCircle} label="Normal Invoices" value="0" note="Awaiting analysis" />
                <Stat icon={AlertTriangle} label="Flagged Invoices" value="0" note="Awaiting analysis" />
                <Stat icon={TrendingUp} label="Shops Profiled" value="0" note="History builds over time" />
              </div>

              <div className="panel-grid">
                <section className="panel upload-panel">
                  <div className="panel-heading">
                    <div><h2>Analyse an Invoice</h2><p>Upload an invoice to begin a compliance review.</p></div>
                    <div className="heading-icon"><Upload /></div>
                  </div>

                  <label className="dropzone">
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={e => setFile(e.target.files?.[0] || null)}
                    />
                    <div className="upload-icon"><Upload size={25} /></div>
                    <strong>{file ? file.name : 'Choose an invoice to upload'}</strong>
                    <span>{file ? `${(file.size / 1024).toFixed(1)} KB` : 'PDF, PNG or JPG · Maximum 10 MB'}</span>
                    <span className="browse-button">Browse files</span>
                  </label>

                  <button
                    className="primary-button"
                    disabled={!file}
                    onClick={() => setActivePage('Invoice Analysis')}
                  >
                    Continue to Analysis <span>→</span>
                  </button>
                  <p className="disclaimer">Analysis will be connected to the backend in a later step.</p>
                </section>

                <section className="panel">
                  <div className="panel-heading">
                    <div><h2>How it works</h2><p>Three stages of invoice review</p></div>
                  </div>
                  <div className="steps">
                    <Step number="01" title="Upload Invoice" text="Select a PDF or invoice image." />
                    <Step number="02" title="Extract & Validate" text="Read invoice fields and check arithmetic." />
                    <Step number="03" title="Review Risk" text="Inspect anomalies and shop history." />
                  </div>
                  <div className="info-note">
                    <ShieldCheck size={20} />
                    <p>AI flags unusual patterns for human review. A flag does not prove fraud.</p>
                  </div>
                </section>
              </div>
            </>
          )}

          
{activePage === 'Invoice Analysis' && (
  <section className="panel">
    <div className="panel-heading">
      <div>
        <h2>Invoice Analysis</h2>
        <p>Enter invoice details to run the trained ML model.</p>
      </div>
    </div>

    <form onSubmit={analyzeInvoice} className="invoice-form">
      {[
        ['invoice_id', 'Invoice ID'],
        ['shop_id', 'Shop ID'],
        ['quantity', 'Quantity'],
        ['unit_price', 'Unit price'],
        ['taxable_value', 'Taxable value'],
        ['gst_rate', 'GST rate (%)'],
        ['gst_amount', 'GST amount'],
        ['total_amount', 'Total amount'],
        ['invoice_age_days', 'Invoice age (days)'],
      ].map(([key, label]) => (
        <label key={key} className="field">
          <span>{label}</span>
          <input
            required
            type={['invoice_id', 'shop_id'].includes(key) ? 'text' : 'number'}
            min={['quantity'].includes(key) ? '0.000001' : '0'}
            step="any"
            value={invoiceData[key]}
            onChange={(event) =>
              setInvoiceData({
                ...invoiceData,
                [key]: event.target.value,
              })
            }
          />
        </label>
      ))}

      <button className="primary-button" disabled={loading} type="submit">
        {loading ? 'Analysing...' : 'Analyse Invoice'}
      </button>
    </form>

    {apiError && <p className="api-error">{apiError}</p>}

    {result && (
      <div className="result-panel">
        <h2>Analysis Result: {result.status}</h2>
        <p>{result.message}</p>
        <p>Model prediction: {result.model_prediction}</p>
        <p>Anomaly score: {result.anomaly_score}</p>

        <h3>Issues detected</h3>
        {result.issues.length > 0 ? (
          <ul>
            {result.issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        ) : (
          <p>No arithmetic inconsistencies detected.</p>
        )}

        <p className="disclaimer">{result.disclaimer}</p>
      </div>
    )}
  </section>
)}


          {activePage === 'Shop History' && (
            <section className="panel empty-panel">
              <History size={36} />
              <h2>Shop Historical Profiles</h2>
              <p>No shop history yet.</p>
              <p>Once invoices are analysed and saved, the system can build shop-specific transaction profiles.</p>
            </section>
          )}

          {activePage === 'Settings' && (
            <section className="panel empty-panel">
              <Settings size={36} />
              <h2>Settings</h2>
              <p>API configuration, upload limits and model settings will be added during integration.</p>
            </section>
          )}

          <footer>GSTGuard-I · AI-assisted GST invoice anomaly detection</footer>
        </section>
      </main>
    </div>
  )
}

function Stat({ icon: Icon, label, value, note }) {
  return (
    <div className="stat-card">
      <div className="stat-top"><span>{label}</span><Icon size={20} /></div>
      <h2>{value}</h2>
      <p>{note}</p>
    </div>
  )
}

function Step({ number, title, text }) {
  return (
    <div className="step">
      <span>{number}</span>
      <div><strong>{title}</strong><p>{text}</p></div>
    </div>
  )
}

export default App
