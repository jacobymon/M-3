
import logo from './logo.svg';
import './App.css';
import { SongSubmission } from './components/SongSubmission';
import DisplayedQueue from './components/WebsiteQueue';


/** The main app of the thing
 * 
 * @returns Nothing but does stuff
 */
function App() {
  return (
    <div className="App">
      
      <header className="App-header">
        <h1>M-3</h1>
      </header>

      <body className="App-body">
        <SongSubmission />
      </body>

    </div>
  );
}

export default App;
