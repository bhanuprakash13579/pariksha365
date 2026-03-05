import React, { useState, useEffect, useRef, useMemo } from 'react';
import { AlertTriangle, Search, Check } from 'lucide-react';

interface TopicCode {
    code: string;
    subject: string;
    topic: string;
}

interface SmartTopicSelectorProps {
    value: string;
    onChange: (code: string) => void;
    topicCodes: TopicCode[];
    hasError: boolean;
    validCodesSet: Set<string>;
}

// Simple but effective subsequence fuzzy matcher e.g., "srt" matches "Straits"
function fuzzyMatch(pattern: string, str: string): boolean {
    let patternIdx = 0;
    let strIdx = 0;
    let patternLength = pattern.length;
    let strLength = str.length;

    // Subsequence match
    while (patternIdx !== patternLength && strIdx !== strLength) {
        if (pattern[patternIdx].toLowerCase() === str[strIdx].toLowerCase()) {
            patternIdx++;
        }
        strIdx++;
    }
    return patternLength !== 0 && strLength !== 0 && patternIdx === patternLength;
}

export const SmartTopicSelector: React.FC<SmartTopicSelectorProps> = ({
    value, onChange, topicCodes, hasError, validCodesSet
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const containerRef = useRef<HTMLDivElement>(null);

    // Initial label
    const selectedTopic = topicCodes.find(tc => tc.code === value);
    const displayValue = selectedTopic ? `${selectedTopic.topic} (${selectedTopic.code})` : value;

    useEffect(() => {
        if (!isOpen) {
            setSearchTerm('');
        }
    }, [isOpen]);

    // Close when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const filteredOptions = useMemo(() => {
        if (!searchTerm) {
            // If nothing searched, maybe show first 50 to avoid lag
            return topicCodes.slice(0, 50);
        }
        const searchLower = searchTerm.toLowerCase();

        // Exact substring matches rank higher
        const exactMatches = topicCodes.filter(tc =>
            tc.topic.toLowerCase().includes(searchLower) ||
            tc.code.toLowerCase().includes(searchLower) ||
            tc.subject.toLowerCase().includes(searchLower)
        );

        // Fuzzy matches (excluding exact ones to avoid duplicates)
        const exactSet = new Set(exactMatches.map(tc => tc.code));
        const fuzzyMatches = topicCodes.filter(tc =>
            !exactSet.has(tc.code) &&
            (fuzzyMatch(searchTerm, tc.topic) || fuzzyMatch(searchTerm, tc.code))
        );

        return [...exactMatches, ...fuzzyMatches].slice(0, 50); // Cap at 50 results
    }, [searchTerm, topicCodes]);

    return (
        <div className="relative" ref={containerRef}>
            <div
                onClick={() => setIsOpen(!isOpen)}
                className={`w-full flex items-center justify-between border p-1.5 rounded text-sm cursor-pointer select-none bg-white 
                    ${hasError ? 'border-red-300 bg-red-50 text-red-900 focus:ring-red-400' : 'border-gray-300 focus:ring-orange-400 text-gray-700'}`}
            >
                <div className="flex-1 truncate">
                    {value ? (
                        validCodesSet.has(value) ? (
                            <span className="font-mono">{displayValue}</span>
                        ) : (
                            <span className="text-red-500 font-bold flex items-center gap-1">
                                <AlertTriangle className="w-4 h-4" /> ❌ "{value}" not found
                            </span>
                        )
                    ) : (
                        <span className="text-gray-400">🔍 Search and select topic code...</span>
                    )}
                </div>
            </div>

            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-72 flex flex-col">
                    <div className="p-2 border-b border-gray-100 flex gap-2 items-center text-gray-400">
                        <Search className="w-4 h-4 shrink-0" />
                        <input
                            autoFocus
                            type="text"
                            className="w-full text-sm outline-none text-gray-700 placeholder-gray-400 bg-transparent"
                            placeholder="Type to search smartly (topic or code)..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <div className="overflow-y-auto flex-1 p-1">
                        {filteredOptions.length === 0 ? (
                            <div className="p-3 text-center text-sm text-gray-500">
                                No topics found. Try broader search.
                            </div>
                        ) : (
                            filteredOptions.map(tc => (
                                <div
                                    key={tc.code}
                                    onClick={() => {
                                        onChange(tc.code);
                                        setIsOpen(false);
                                    }}
                                    className={`px-3 py-2 text-sm cursor-pointer rounded-md flex items-center justify-between
                                        ${value === tc.code ? 'bg-orange-50 text-orange-700 font-medium' : 'hover:bg-gray-100 text-gray-700'}`}
                                >
                                    <div>
                                        <div className="font-medium">{tc.topic}</div>
                                        <div className="text-xs opacity-75">{tc.subject} &bull; <span className="font-mono">{tc.code}</span></div>
                                    </div>
                                    {value === tc.code && <Check className="w-4 h-4 text-orange-600" />}
                                </div>
                            ))
                        )}
                        {searchTerm === '' && topicCodes.length > 50 && (
                            <div className="px-3 py-2 text-xs text-center text-gray-400 border-t border-gray-50">
                                Start typing to search across {topicCodes.length} topics.
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
