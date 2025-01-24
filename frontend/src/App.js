import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Song from './pages/Song';
import Profile from './pages/Profile';
import Header from './components/Header';

function App() {
    return (
        <Router>
            <Header />
            <Switch>
                <Route exact path="/" component={Home} />
                <Route path="/upload" component={Upload} />
                <Route path="/song/:id" component={Song} />
                <Route path="/profile" component={Profile} />
            </Switch>
        </Router>
    );
}

export default App;
