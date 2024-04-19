
import logo from './logo.svg';
import './App.css';
import { SongSubmission } from './components/SongSubmission';
import MyComponent from './modules/TestComponent/myComponent';
import DisplayedQueue from './components/WebsiteQueue';


/** The main app of the thing
 * 
 * @returns Nothing but does stuff
 */
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
        <SongSubmission />
      </header>
    </div>
  );
}

export default App;
