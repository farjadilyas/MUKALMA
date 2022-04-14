import React, { useState, useEffect } from "react";

import { Container } from '@material-ui/core'
import { BrowserRouter, Switch, Route } from "react-router-dom";

import Navbar from "./components/Navbar/Navbar";
import Home from "./components/Home/Home";
import SplashScreen from './components/SplashScreen/SplashScreen'

import './App.css'

// Main App Code
const App = () => {
    // Loading state variable
    const [isLoading, setIsLoading] = useState(true);

    // Waiting for 3 seconds before routing to main
    useEffect(() => {
        setTimeout(() => {
            setIsLoading(false);
        }, 4700);
    }, []);


    // Main Website Return
    return isLoading ? <SplashScreen /> :
    (
        <BrowserRouter>
            <Container className="mainContainer" maxWidth={false}>
                <Navbar />
                <Switch>
                    <Route path="/" exact component={Home}/>
                </Switch>
            </Container>
        </BrowserRouter>
    )
}

export default App;
