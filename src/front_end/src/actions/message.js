import * as api from '../api'
import { agent, initialState } from '../components/Chatbox/state'
import { scrollToHighlight } from '../components/Source/scroll'
import { scrollToBottom } from '../components/Chatbox/Chatbox'

export const sendMessage = (
    message,
    isAsync,
    setMessages, 
    setSource,
    setSpanSelected, 
    setResponses, 
    setSpeechText,
    messages, 
    setShowProgress,
    setPaddingBottom,
    setResponseProgressMessage,
    setActiveStep,
    setTopics,
    messageId,
    setMessageId
    ) => async () => {

    try {
        const messageUpdates = ["Knowledge Fetched from article", "Knowledge Span Extracted", "Cloze Completion completed!"];

        // Setting Ticker Timers
        for (let i = 1; i <= 3; i++) {
            setTimeout(() => {
                setActiveStep(i);
                setResponseProgressMessage(messageUpdates[i]);
            }, i * 1000);
        }

        // First call for message reply
        let data = await api.sendMessage(message)

        // Setting State after Sync call
        if (!isAsync) {        
            // Setting final progress element
            setActiveStep(4);
            setResponseProgressMessage(data.data.message);

            // Checking for message Ids
            let m_id = data.data.m_id;
            while (m_id !== messageId) {
                data = await api.sendMessage(message);
                m_id = data.data.m_id;
            }

            setMessageId(messageId + 1);

            // Getting Conversation Response
            var result = data.data.response;
            var responseList = result.split(".");

            // Pausing for a second before updating everything
            setTimeout(() => {

                // Setting the source
                var source = data.data.knowledge_source;
                setSource(source);

                // Adding Multiple messages based on the full stops
                // Each sentence is uttered as a separate text message
                var i
                for (i = 0; i < responseList.length - 1; ++i) 
                {
                    if (responseList[i].length > 0) {
                        setMessages(messages => [...messages, {
                            "text": responseList[i],
                            "id": "0",
                            "sender": agent
                        }]);
                    }
                }

                // Setting Topics and keywords
                setTopics(topics => [...topics, {
                    "knowledge_article": data.data.topic.knowledge_article,
                    "keywords": data.data.topic.keywords
                }])

                // Setting Span of text by Q/A
                var span = data.data.knowledge_sent
                setSpanSelected(span)

                // Setting Candidate Responses
                var responses = data.data.candidates
                setResponses(responses)

                // Updating UI
                setPaddingBottom(0);
                setShowProgress(false);
                setActiveStep(0)
                setResponseProgressMessage('Fetching knowledge source ...')
                // scrollToHighlight(messages.length);

                // Setting Audio
                setSpeechText(result);
            }, 1000);
        }
    } catch (error) {
        console.log(error);
    }
}

export const clearContext = () => async () => {
    try {
        const data = await api.clearContext();
    } catch (error) {
        console.log(error);
    }
}

export const connectToApi = (setConnectionStatus) => async () => {
    try {
        const data = await api.connect();
        data ? setConnectionStatus(true) : setConnectionStatus(false);
    } catch (error) {
        console.log(error);
    }
}

export const waitForResponse = (
        setMessages, 
        setSource,
        setSpanSelected, 
        setResponses, 
        setSpeechText,
        messages, 
        setShowProgress,
        setPaddingBottom,
        setResponseProgressMessage,
        setActiveStep,
        setTopics
    ) => async () => {
    try {

        // For Debugging Only
        // Debugging Starts
        // setTimeout(() => {
        //     setMessages(messages => [...messages, {
        //         "text": "Sorry!",
        //         "id": "0",
        //         "sender": agent
        //     }]);
        //     setMessages(messages => [...messages, {
        //         "text": "I can't answer your question right now!",
        //         "id": "0",
        //         "sender": agent
        //     }]);
        //     setMessages(messages => [...messages, {
        //         "text": "Please try again later",
        //         "id": "0",
        //         "sender": agent
        //     }]);

        //     setTopics(topics => [...topics, {
        //         "knowledge_article": "Karachi",
        //         "keywords": ["karachi", "city", "pakistan", "beach"]
        //     }])
            
        //     // setSpeechText("Sorry! I can't answer your question right now! Please try again later");
        //     setPaddingBottom(0);
        //     setShowProgress(false);

        // }, 3000);
        // Debugging Ends

        // Production Code Starts

        // First call for knowledge selection
        for (let i = 0; i < 3; ++i) {
            var data = await api.waitForResponse()
            setResponseProgressMessage(data.data.message)
            setActiveStep(i)
        }
        
        // Retrieving Data for Final Response
        setActiveStep(3);
        var data = await api.waitForResponse();

        // Setting final progress element
        setActiveStep(4);
        setResponseProgressMessage(data.data.message);

        // Getting Conversation Response
        var result = data.data.response;
        var responseList = result.split(".");

        // Pausing for a second before updating everything
        setTimeout(() => {

            // Setting the source
            var source = data.data.knowledge_source;
            setSource(source);

            // Adding Multiple messages based on the full stops
            // Each sentence is uttered as a separate text message
            var i
            for (i = 0; i < responseList.length - 1; ++i) 
            {
                if (responseList[i].length > 0) {
                    setMessages(messages => [...messages, {
                        "text": responseList[i],
                        "id": "0",
                        "sender": agent
                    }]);
                }
            }

            // Setting Topics and keywords
            setTopics(topics => [...topics, {
                "knowledge_article": data.data.topic.knowledge_article,
                "keywords": data.data.topic.keywords
            }])

            // Setting Span of text by Q/A
            var span = data.data.knowledge_sent
            setSpanSelected(span)

            // Setting Candidate Responses
            var responses = data.data.candidates
            setResponses(responses)

            // Updating UI
            setPaddingBottom(0);
            setShowProgress(false);
            setActiveStep(0)
            setResponseProgressMessage('Fetching knowledge source ...')
            // scrollToHighlight(messages.length);

            // Setting Audio
            setSpeechText(result);
        }, 1000)

        // Production Code Ends
    } catch (error) {
        console.log(error)
    }
}
