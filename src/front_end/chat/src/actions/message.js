import * as api from '../api'
import { agent, initialState } from '../components/Chatbox/state'
import { hideTyping } from '../components/Chatbox/TypingIndicator/setTyping'
import { scrollToHighlight } from '../components/Source/scroll'
import { scrollToBottom } from '../components/Chatbox/Chatbox'

// Function
export const sendMessage = (
        message, 
        setMessages, 
        setSource,
        setSpanSelected, 
        setResponses, 
        setSpeechText,
        messages, 
        setShowProgress,
        setPaddingBottom
    ) => async () => {
    try {

        // For Debugging Only
        // Debugging Starts
        setTimeout(() => {
            setMessages(messages => [...messages, {
                "text": "Sorry!",
                "id": "0",
                "sender": agent
            }]);
            setMessages(messages => [...messages, {
                "text": "I can't answer your question right now!",
                "id": "0",
                "sender": agent
            }]);
            setMessages(messages => [...messages, {
                "text": "Please try again later",
                "id": "0",
                "sender": agent
            }]);
            
            // setSpeechText("Sorry! I can't answer your question right now! Please try again later");
            setPaddingBottom(0);
            setShowProgress(false);

        }, 3000);
        // Debugging Ends

        // const data = await api.sendMessage(message)
        // console.log(data);

        // // Retrieving Data
        // var result = data.data.response
        // var responseList = result.split(".")

        // // Setting the source
        // var source = data.data.knowledge_source;
        // setSource(source);

        // // Adding Multiple messages based on the full stops
        // // Each sentence is uttered as a separate text message
        // var i
        // for (i = 0; i < responseList.length - 1; ++i) 
        // {
        //     if (responseList[i].length > 0) {
        //         setMessages(messages => [...messages, {
        //             "text": responseList[i],
        //             "id": "0",
        //             "sender": agent
        //         }]);
        //     }
        // }

        // // Setting Span of text by Q/A
        // var span = data.data.knowledge_sent
        // setSpanSelected(span)

        // // Setting Candidate Responses
        // var responses = data.data.candidates
        // setResponses(responses)
        
        // // Updating UI
        // hideTyping();
        // scrollToHighlight(messages.length);

        // // Setting Audio
        // setSpeechText(result);
        
    } catch (error) {
        console.log(error)
    }
}

export const fetchSource = (setSource) => async () => {
    try {
        const data = await api.fetchSource()
        setSource(data.data.response)
    } catch (error) {
        console.log(error)
    }
}

export const fetchTopics = (setTopic, setTopics) => async () => {
    try {
        const data = await api.fetchTopics()
        setTopic(data.data.current_topic)
        setTopics(data.data.topics)
    } catch (error) {
        console.log(error)
    }
}

export const topicSelect = (topic, setSource, setMessages, setProgress) => async (dispatch) => {
    try {
        const data = await api.changeTopic({"topic": topic});
        if (data.status === 200) {
            dispatch(fetchSource(setSource))
            setMessages(initialState)
            setProgress("hidden")
        } else {
            throw Error
        }
    } catch (error) {
        console.log(error)
    }
}
