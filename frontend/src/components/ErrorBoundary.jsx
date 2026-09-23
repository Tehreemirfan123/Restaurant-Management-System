import { Component } from "react";

// Catches render-time errors anywhere below it so a single broken component
// shows a friendly fallback instead of white-screening the whole app.
export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error, info) {
        // Log for diagnostics; in production wire this to an error tracker.
        console.error("Uncaught UI error:", error, info);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-cream-100 p-6">
                    <div className="bg-white rounded-2xl shadow-md p-8 max-w-md text-center">
                        <h1 className="text-xl font-bold text-maroon-800">
                            Something went wrong
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Please refresh the page. If it keeps happening,
                            contact us on WhatsApp.
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="mt-5 bg-maroon-700 hover:bg-maroon-800 text-white font-semibold py-2.5 px-5 rounded-lg"
                        >
                            Refresh
                        </button>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}
