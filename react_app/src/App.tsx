import * as React from 'react';
import * as CodeMirror from 'react-codemirror';
import Textarea from 'react-textarea-autosize';
import './App.css';
import { runCommand, getPrompt } from './api_services';

require('codemirror/lib/codemirror.css');

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
  prompt?: string;
  stdout?: string;
  content?: string;
  path?: string;
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
    const prompt = await getPrompt();
    this.setState({ prompts: [prompt] });
  }

  runCommand = async (request: string) => {
    let prompts = this.state.prompts;
    let requests = this.state.requests;
    let results = this.state.results;

    if (request.split(' ')[0].toLowerCase() === 'clear') {
      this.setState({prompts: [prompts[prompts.length - 1]], requests: [], results: []});
      return;
    }

    const response = await runCommand(request) as Response;
    if (response.context === 'terminal') { 
      requests.push(request);
      prompts.push(response.prompt!);
      results.push(response.stdout!);
      this.setState({
        context: response.context, 
        prompts: prompts, 
        requests: requests, 
        results: results, 
      });
    }

    if (response.context === 'editor') {
      this.setState({
        context: response.context, 
        editorContent: response.content!,
        editorPath: response.path!
      });
    }
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

  renderEditor = () => {
    return (
      <div id="editor">
        <div className="actions">
          <button onClick={this.handleEditOnExit}>Exit</button>
          <button onClick={this.handleEditOnSave}>Save</button>
        </div>
        <CodeMirror 
          value={this.state.editorContent}
          onChange={(v) => this.setState({editorContent: v})}
          options={{lineNumbers: true}}
        />
      </div>
    );
  }

  handleEditOnExit = () => {
    this.setState({context: 'terminal'});
  }

  handleEditOnSave = () => {
    const path = this.state.editorPath;
    const content = this.state.editorContent;
    this.runCommand(`save "${ path }" "${ content }"`);
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
            {this.renderEditor()}
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
