import * as React from 'react';

import { EditorResult } from './api_services';
import EditorContext from './contexts/editor';
import TerminalContext from './contexts/terminal';

import './App.css';

interface AppProps { }

interface AppState {
  contexts: Array<JSX.Element>;
}

class App extends React.Component<AppProps, AppState> {

  constructor(props: AppProps) {
    super(props);
    this.state = {
      contexts: []
    };
  }

  pushContext = (response: any) => {
    let contexts = this.state.contexts;
    if (response.context === 'editor') {
      response = response as EditorResult;
      contexts.push(<EditorContext path={response.path} content={response.content} exit={this.exitContext} />);
    }
    this.setState({contexts: contexts});
  }

  exitContext = () => {
    let contexts = this.state.contexts;
    contexts.pop();
    this.setState({contexts: contexts});
  }

  render() {
    if (this.state.contexts.length === 0) {
      this.setState({
        contexts: [<TerminalContext key="1" pushContext={this.pushContext} />]
      });
    }

    return <div className="App">{this.state.contexts[this.state.contexts.length - 1]}</div>;        
  }
}

export default App;
