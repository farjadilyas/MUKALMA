import React, { useState, useEffect } from "react";

import { Container } from '@material-ui/core'
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { values } from "./constants";

import { Navbar, Home, SplashScreen } from './components'

import './App.css'

// Main App Code
const App = () => {

    // Loading state variable
    const [isLoading, setIsLoading] = useState(true);

    // Reply
    const [asyncApi, setAsyncApi] = useState(true);

    // Waiting for animation timeout seconds before routing to main
    useEffect(() => {
        setTimeout(() => {
            setIsLoading(false);
        }, values.SPLASH_SCREEN_ANIMATION_TIMEOUT);
    }, []);


    // Main Website Return
    return isLoading ? <SplashScreen /> :
    (
        <Container className="mainContainer" maxWidth={false}>
            <Navbar asyncApi={asyncApi} setAsyncApi={setAsyncApi} />
            <Home asyncApi={asyncApi} />
        </Container>
    );
}

export default App;
