import {useEffect, useRef} from "react";


export function useAutoScroll(messages) {
    const bottomRef = useRef(null)
    useEffect(() => {
        bottomRef.current?.scrollIntoView({behavior: "smooth"})
    }, [messages])
    return bottomRef
}