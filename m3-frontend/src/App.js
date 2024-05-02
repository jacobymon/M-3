import './App.css';
import QRCode from "./content/qr-code.png"
import { SongSubmission } from './components/SongSubmission';
import DisplayedQueue from './components/WebsiteQueue';
import { useState } from 'react';

const qr_code_link = `http://${process.env.REACT_APP_BACKEND_IP}:3000`

/** The main app of the thing
 * 
 * @returns Nothing but does stuff
 */
function App() {

  const [largeQR, setLargeQR] = useState(false);
  
  const toggleQRSize = () => {
    setLargeQR(!largeQR);
  };

  return (
    <div className="App">

      <header className="App-header">
        {!largeQR &&
          <h1 className='h1-mt'>M-3</h1>
        }
        {largeQR &&
          <div>
            <h1 className='h1-mt'>
              <a className="join-the-party" href={qr_code_link}>Join the Party!</a>
            </h1>
          </div>
        }
          
      </header>

      <img className={`qr-code ${largeQR ? 'large' : 'small'}`}
              src={QRCode} 
              alt="QR Code"
              onClick={toggleQRSize}/>

      <div className="App-body">
        
        <SongSubmission />
        <DisplayedQueue />
      </div>

    </div>
  );
}

export default App;
