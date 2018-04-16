import * as React from 'react';
import Textarea from 'react-textarea-autosize';
import './App.css';

interface AppProps { }

interface AppState {
  prompts: Array<string>;
  requests: Array<string>;
  results: Array<string>;
}

interface CommandPromptProps {
  i: number;
  prompt: string;
  request?: string;
  history: Array<string>;
  runCommand: (request: string) => void;
}

interface CommandPromptState { }

interface CommandResultProps { 
  result: string;
}

interface CommandResultState { } 

interface Response {
  nextPrompt: string;
  result: string;
}

class CommandResult extends React.Component<CommandResultProps, CommandResultState> {
  
  constructor(props: CommandResultProps) {
    super(props);
  }

  render() {
    return (
      <div>
        <pre>{this.props.result}</pre>
      </div>
    );
  }
}

class CommandPrompt extends React.Component<CommandPromptProps, CommandPromptState>  {

  private commandTextArea: HTMLTextAreaElement | null = null;
  private historyPosition: number;

  constructor(props: CommandPromptProps) {
    super(props);
    this.historyPosition = props.history.length;
  }

  componentDidMount() {
    if (this.commandTextArea) {
      this.commandTextArea.focus();
    }
  }

  public inputRef = (ref: HTMLTextAreaElement) => {
    this.commandTextArea = ref;
  }

  handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.ctrlKey) {
      event.preventDefault();
      if (this.commandTextArea) {
        this.props.runCommand(this.commandTextArea.value);
      }
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {

      if (event.key === 'ArrowUp') {
        if (this.historyPosition > 0) {
          this.historyPosition -= 1;
        }
      }

      if (event.key === 'ArrowDown') {
        if (this.historyPosition < this.props.history.length) {
          this.historyPosition += 1;
        }  
      }

      if (this.commandTextArea) {
        if (this.historyPosition === this.props.history.length) {
          this.commandTextArea.value = '';
        } else {
          this.commandTextArea.value = this.props.history[this.historyPosition];
        }
      }
    }

  }

  renderRequest = () => {
    if (this.props.request) {
      return <Textarea rows={1} disabled={true} defaultValue={this.props.request} />;
    } else {
      return (
        <Textarea 
          autoCapitalize="none"
          onKeyPress={this.handleKeyPress}
          onKeyDown={this.handleKeyPress}
          rows={1}
          inputRef={this.inputRef}
        />
      );
    }
  }

  render() {
    return (
      <div>
        <div>{this.props.prompt}</div>
        <div>
          {this.renderRequest()}
        </div>
      </div>
    );
  }
}

class App extends React.Component<AppProps, AppState> {

  private lastCommandPrompt: CommandPrompt | null = null;
  private history: Array<string> = [];

  constructor(props: AppProps) {
    super(props);
    this.state = {
      prompts: [],
      requests: [],
      results: []
    };
    this.getInitialPrompt();
  }

  getInitialPrompt = async () => {
    fetch('/prompt', {
      credentials: 'same-origin'  
    })
    .then(r => r.text())
    .then(t => this.setState({prompts: [t], requests: [], results: []}));
  }

  runCommand = (request: string) => {
    let prompts = this.state.prompts;
    let requests = this.state.requests;
    let results = this.state.results;

    if (request.split(' ')[0].toLowerCase() === 'clear') {
      this.setState({prompts: [prompts[prompts.length - 1]], requests: [], results: []});
      return;
    }

    fetch('/run', {
      method: 'POST', 
      headers: {'content-type': 'application/json;'},
      credentials: 'same-origin',
      body: JSON.stringify({ command: request })
    })
    .then( r => r.json() )
    .then( data => {
      const response = data as Response;
      this.history.push(request);
      requests.push(request);
      prompts.push(response.nextPrompt);
      results.push(response.result);
      this.setState({prompts: prompts, requests: requests, results: results});
    })
    .catch( e => {
      requests.push(request);
      prompts.push(prompts[prompts.length - 1]);
      results.push(e.responseText);
      this.setState({prompts: prompts, requests: requests, results: results});
    });
  }

  renderPrompt = (i: number, includeRequest: boolean) => {
    const prompt = this.state.prompts[i];
    if (includeRequest) {
      return (
        <CommandPrompt
          i={i}
          prompt={prompt}
          request={this.state.requests[i]}
          history={this.history}
          runCommand={this.runCommand}
        />
      );
    }
    return (
      <CommandPrompt
        i={i}
        prompt={prompt}
        runCommand={this.runCommand}
        history={this.history}
        ref={r => this.lastCommandPrompt = r}
      />
    );
  }

  renderResult = (i: number) => {
    const result = this.state.results[i];
    return (
      <CommandResult result={result} />
    );
  }

  renderCommands = () => {
    let listItems = Array.from(Array(this.state.results.length).keys()).map( i => 
      <li key={i}>{this.renderPrompt(i, true)}{this.renderResult(i)}</li>
    );

    listItems.push(<li>{this.renderPrompt(this.state.results.length, false)}</li>);

    return listItems;
  }

  render() {
    return (
      <div className="App">
        <ul>{this.renderCommands()}</ul>
      </div>
    );
  }
}

export default App;
