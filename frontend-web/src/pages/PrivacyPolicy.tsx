import React from 'react';

export const PrivacyPolicy: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl w-full bg-white shadow-xl rounded-2xl p-8 space-y-6">
                <h1 className="text-3xl font-extrabold text-gray-900 border-b pb-4">Privacy Policy</h1>

                <p className="text-sm text-gray-500">Last updated: {new Date().toLocaleDateString()}</p>

                <div className="space-y-4 text-gray-700">
                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">1. Introduction</h2>
                        <p>
                            Welcome to Pariksha365. We respect your privacy and are committed to protecting your personal data.
                            This privacy policy will inform you as to how we look after your personal data when you visit our website
                            or use our mobile application and tell you about your privacy rights and how the law protects you.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">2. Data We Collect</h2>
                        <p>We may collect, use, store and transfer different kinds of personal data about you which we have grouped together as follows:</p>
                        <ul className="list-disc pl-5 mt-2 space-y-1">
                            <li><strong>Identity Data:</strong> includes first name, last name, username or similar identifier.</li>
                            <li><strong>Contact Data:</strong> includes email address and telephone numbers.</li>
                            <li><strong>Technical Data:</strong> includes internet protocol (IP) address, your login data, browser type and version.</li>
                            <li><strong>Usage Data:</strong> includes information about how you use our app, test completion statistics, and scores.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">3. How We Use Your Data</h2>
                        <p>We will only use your personal data when the law allows us to. Most commonly, we will use your personal data in the following circumstances:</p>
                        <ul className="list-disc pl-5 mt-2 space-y-1">
                            <li>To register you as a new user.</li>
                            <li>To process and deliver your mock test results.</li>
                            <li>To manage our relationship with you.</li>
                            <li>To improve our website, products/services, marketing or customer relationships.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">4. Data Security</h2>
                        <p>
                            We have put in place appropriate security measures to prevent your personal data from being accidentally lost, used or accessed in an unauthorized way, altered or disclosed.
                            In addition, we limit access to your personal data to those employees, agents, contractors and other third parties who have a business need to know.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">5. Your Legal Rights</h2>
                        <p>Under certain circumstances, you have rights under data protection laws in relation to your personal data. These include the right to:</p>
                        <ul className="list-disc pl-5 mt-2 space-y-1">
                            <li>Request access to your personal data.</li>
                            <li>Request correction of your personal data.</li>
                            <li>Request erasure of your personal data.</li>
                            <li>Object to processing of your personal data.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-gray-900 mt-6 mb-2">6. Contact Us</h2>
                        <p>If you have any questions about this privacy policy or our privacy practices, please contact us at standard contact email address for developers.</p>
                    </section>
                </div>
            </div>
        </div>
    );
};
