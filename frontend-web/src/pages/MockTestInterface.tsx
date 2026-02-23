import { useState } from 'react';

export const MockTestInterface = () => {
    const [selectedOption, setSelectedOption] = useState<number | null>(null);

    return (
        <div className="flex flex-col h-screen bg-white">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 bg-gray-800 text-white">
                <h1 className="text-xl font-bold">SSC CGL Tier 1 Full Mock Test</h1>
                <div className="flex space-x-4 items-center">
                    <span className="bg-red-500 px-3 py-1 rounded text-sm font-bold animate-pulse">
                        Time Left: 43:12
                    </span>
                    <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-bold transition-colors">
                        Submit Test
                    </button>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                {/* Main Content Area */}
                <main className="flex-1 flex flex-col border-r border-gray-200">
                    <div className="flex border-b border-gray-200">
                        {['Quantitative Aptitude', 'Reasoning', 'English', 'General Awareness'].map((section, idx) => (
                            <button
                                key={idx}
                                className={`px-4 py-3 text-sm font-medium ${idx === 0 ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
                            >
                                {section}
                            </button>
                        ))}
                    </div>

                    <div className="p-8 flex-1 overflow-y-auto">
                        <div className="flex justify-between text-sm text-gray-500 mb-6">
                            <span>Question 1.</span>
                            <span>Marks: +2 / -0.5</span>
                        </div>

                        <h2 className="text-lg font-medium text-gray-800 mb-6">
                            If a sum of money doubles itself in 5 years at simple interest, what is the rate of interest?
                        </h2>

                        <div className="space-y-4">
                            {['10%', '15%', '20%', '25%'].map((opt, i) => (
                                <label key={i} className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${selectedOption === i ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50 border-gray-200'}`}>
                                    <input
                                        type="radio"
                                        name="option"
                                        className="w-4 h-4 text-blue-600 cursor-pointer"
                                        checked={selectedOption === i}
                                        onChange={() => setSelectedOption(i)}
                                    />
                                    <span className="ml-3 text-gray-700">{opt}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Footer Controls */}
                    <footer className="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50">
                        <div className="space-x-4">
                            <button className="px-6 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-100 transition-colors">Mark for Review & Next</button>
                            <button className="px-6 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-100 transition-colors" onClick={() => setSelectedOption(null)}>Clear Response</button>
                        </div>
                        <button className="px-8 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition-colors">Save & Next</button>
                    </footer>
                </main>

                {/* Right Sidebar - Palette */}
                <aside className="w-80 bg-gray-50 p-6 flex flex-col">
                    <div className="flex items-center space-x-3 mb-6">
                        <img src="https://ui-avatars.com/api/?name=Student&background=random" className="w-12 h-12 rounded-full" alt="Profile" />
                        <div>
                            <p className="font-semibold text-gray-800">Student Name</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                        <div className="flex items-center"><div className="w-6 h-6 rounded-l-full rounded-r-full bg-green-500 mr-2 text-white flex justify-center items-center text-xs">5</div> Answered</div>
                        <div className="flex items-center"><div className="w-6 h-6 rounded-l-full rounded-r-full bg-red-500 mr-2 text-white flex justify-center items-center text-xs">12</div> Not Answered</div>
                        <div className="flex items-center"><div className="w-6 h-6 rounded-full border border-gray-300 bg-white mr-2 text-gray-600 flex justify-center items-center text-xs">8</div> Not Visited</div>
                        <div className="flex items-center"><div className="w-6 h-6 rounded-full bg-purple-500 mr-2 text-white flex justify-center items-center text-xs">3</div> Marked Review</div>
                    </div>

                    <h3 className="font-semibold mb-4 border-b pb-2">Quantitative Aptitude</h3>
                    <div className="grid grid-cols-5 gap-2 flex-1 overflow-y-auto content-start">
                        {[...Array(25)].map((_, i) => (
                            <button
                                key={i}
                                className={`w-10 h-10 rounded text-sm font-medium ${i === 0 ? 'bg-green-500 text-white rounded-l-full rounded-r-full' :
                                    i === 1 ? 'bg-red-500 text-white rounded-l-full rounded-r-full' :
                                        i === 2 ? 'bg-purple-500 text-white rounded-full' :
                                            'bg-white border border-gray-300 text-gray-700 rounded-full hover:bg-gray-100'
                                    }`}
                            >
                                {i + 1}
                            </button>
                        ))}
                    </div>
                </aside>
            </div>
        </div>
    );
};
