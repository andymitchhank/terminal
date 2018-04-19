import * as React from 'react';
import * as brace from 'brace';
import AceEditor from 'react-ace';
import Textarea from 'react-textarea-autosize';
import './App.css';

import 'brace/mode/markdown';
import 'brace/theme/github';

interface AppProps { }

interface AppState {
  context: string;
  prompts: Array<string>;
  requests: Array<string>;
  results: Array<string>;
  editorContent: string;
  editorPath: string;
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
  context: string;
  nextPrompt: string;
  result: string;
  editorContent: string;
  editorPath: string;
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
      context: 'terminal',
      editorContent: '',
      prompts: [],
      requests: [],
      results: [],
      editorPath: ''
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
      this.setState({
        context: response.context, 
        prompts: prompts, 
        requests: requests, 
        results: results, 
        editorContent: response.editorContent,
        editorPath: response.editorPath
      });
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

  handleEditOnExit = () => {
    this.setState({context: 'terminal'});
  }

  handleEditOnSave = () => {
    fetch('/save', {
      method: 'POST',
      headers: {'content-type': 'application/json;'},
      credentials: 'same-origin',
      body: JSON.stringify({ path: this.state.editorPath, content: this.state.editorContent })      
    })
    .catch( e => {
      alert(e);
    });
  }

  render() {

    switch (this.state.context) {
      case 'terminal':
        return (
          <div className="App">
            <ul>{this.renderCommands()}</ul>
          </div>
        );

      case 'editor':
        return (
          <div className="App">
            <div className="actions">
              <button onClick={this.handleEditOnExit}>Exit</button>
              <button onClick={this.handleEditOnSave}>Save</button>
            </div>
            <AceEditor 
              mode="markdown"
              theme="github"
              editorProps={{$blockScrolling: true}}
              value={this.state.editorContent}
              onChange={(v) => this.setState({editorContent: v})}
            />
          </div>
        );

      default:
        return (
          <div className="App" />
        );
    }
  }
}

export default App;
