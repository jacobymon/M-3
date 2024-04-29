import './App.css';
import QRCode from "./qr-code.png"
import { SongSubmission } from './components/SongSubmission';
import DisplayedQueue from './components/WebsiteQueue';
import { useState } from 'react';

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
              <a className="join-the-party" href="https://en.wikipedia.org/wiki/List_of_HTTP_status_codes" >Join the Party!</a>
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
        <DisplayedQueue isHost="false" cookie="" />
      </div>

    </div>
  );
}

export default App;
