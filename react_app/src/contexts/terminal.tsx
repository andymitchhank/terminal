import * as React from 'react';
import Textarea from 'react-textarea-autosize';

import { runCommand, getPrompt, TerminalResult } from '../api_services';

interface CommandPromptProps {
  i: number;
  prompt: string;
  request?: string;
  runCommand: (request: string) => void;
}

interface CommandPromptState { }

interface CommandResultProps { 
  result: string;
}

interface CommandResultState { } 

class CommandPrompt extends React.Component<CommandPromptProps, CommandPromptState>  {

  private commandTextArea: HTMLTextAreaElement | null = null;

  constructor(props: CommandPromptProps) {
    super(props);
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

interface Props { 
  pushContext: (response: any) => void;
}

interface State {
  prompts: Array<string>;
  requests: Array<string>;
  results: Array<string>;
}

class TerminalContext extends React.Component<Props, State> {
  
  private lastCommandPrompt: CommandPrompt | null = null;
  
  constructor(props: Props) {
    super(props);
    this.state = {
      prompts: [],
      requests: [],
      results: []
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

    let response = await runCommand(request);
    if (response.context !== 'terminal') {
      this.props.pushContext(response);
    } else {
      response = response as TerminalResult; 
      requests.push(request);
      prompts.push(response.prompt);
      results.push(response.stdout);
      this.setState({
        prompts: prompts, 
        requests: requests, 
        results: results, 
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
          runCommand={this.runCommand}
        />
      );
    }
    return (
      <CommandPrompt
        i={i}
        prompt={prompt}
        runCommand={this.runCommand}
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
    return <ul>{this.renderCommands()}</ul>;
  }
}

export default TerminalContext;
