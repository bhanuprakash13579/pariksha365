import React from 'react';

export const PrivacyPolicy: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl w-full bg-white shadow-2xl rounded-2xl p-8 sm:p-12 space-y-8 text-gray-800">
                <div className="text-center border-b pb-6 mb-8">
                    <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Privacy Policy & Comprehensive Legal Terms</h1>
                    <p className="mt-4 text-sm text-gray-500 font-medium uppercase tracking-wider">Effective Date: {new Date().toLocaleDateString()}</p>
                </div>

                <div className="space-y-8 text-sm leading-relaxed">

                    <section className="bg-blue-50 p-6 rounded-lg border border-blue-100">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">1. Acceptance of Terms</h2>
                        <p>
                            By accessing, browsing, or using the Pariksha365 platform, including our website, mobile applications, mock tests, PDF notes, video lectures, and related services (collectively, the "Services"), you acknowledge that you have read, understood, and agree to be legally bound by this Privacy Policy and all incorporated terms. If you do not agree to these terms, you must immediately cease use of our Services.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">2. Information We Collect</h2>
                        <p className="mb-3">We collect information to provide better services to our users. The types of data we collect include:</p>
                        <ul className="list-disc pl-5 mt-2 space-y-2 text-gray-700">
                            <li><strong>Personal Identity Data:</strong> Names, email addresses, phone numbers, profile images, and login credentials.</li>
                            <li><strong>Usage & Performance Data:</strong> Mock test scores, attempt histories, time spent per question, learning patterns, device information, IP addresses, and browser types.</li>
                            <li><strong>Financial Data:</strong> Transactions are processed via secure third-party payment gateways. We do not store full credit card details on our servers.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">3. How We Use and Share Information</h2>
                        <p className="mb-3">We utilize your data for the core functionality of the platform, service improvement, academic analytics, and direct communication.</p>
                        <b className="block mt-4 mb-2 text-gray-900">Third-Party Sharing & Affiliates</b>
                        <p>
                            We may share aggregated, non-personally identifiable information publicly and with our partners. We reserve the right to transfer all user data in connection with a corporate merger, consolidation, restructuring, or sale of assets, without prior consent. We may also disclose data to satisfy any applicable law, regulation, legal process, or enforceable governmental request.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">4. Account and Data Deletion</h2>
                        <b className="block mb-2 font-bold text-gray-900">Right to Erasure</b>
                        <p className="mb-4 text-gray-700">
                            You have the right to request the complete deletion of your personal data and account at any time. We provide an automated path for account deletion directly inside the Pariksha365 App.
                        </p>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">How to Delete Your Account & Associated Data:</h3>
                        <ol className="list-decimal pl-5 mt-2 mb-4 space-y-2 text-gray-700">
                            <li>Open the Pariksha365 mobile application.</li>
                            <li>Tap on the <strong>Profile</strong> icon or navigate to the <strong>Settings</strong> menu.</li>
                            <li>Tap the red <strong>Delete Account</strong> button at the bottom of the screen.</li>
                            <li>Confirm your request when prompted.</li>
                        </ol>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Data Retention Policy:</h3>
                        <ul className="list-disc pl-5 mt-2 space-y-2 text-gray-700">
                            <li><strong>Immediate Deletion:</strong> Your personal profile, email, authentication tokens, and device identifiers are wiped from our active databases immediately upon request.</li>
                            <li><strong>Aggregated Retention:</strong> Anonymous, aggregated test attempt data (stripped of any personally identifiable information) may be retained for analytical purposes to calculate historical percentiles.</li>
                            <li><strong>Backup Lifecycle:</strong> Your encrypted data may persist in routine secure system backups for up to 90 days before being completely purged.</li>
                        </ul>
                    </section>

                    {/* CRITICAL SECTION FOR USER'S REQUEST */}
                    <section className="bg-red-50 p-6 rounded-lg border border-red-100 mt-10">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">5. Content Disclaimer & Intermediary Status (Safe Harbor)</h2>
                        <p className="mb-4">
                            <strong>Platform as an Intermediary:</strong> Pariksha365 operates strictly as an "Intermediary" as defined under the Information Technology Act, 2000 (and subsequent amendments). Materials available on this platform, including but not limited to mock tests, syllabus breakdowns, current affairs updates, video lectures, objective questions, PDF study notes, and textual explanations, are aggregated, sourced, or independently created by various third-party educators, freelancers, and subject matter experts ("Content Providers").
                        </p>
                        <p className="mb-4 font-bold text-red-800">
                            Pariksha365 explicitly disclaims any ownership over third-party generated content. We do not pre-screen, verify, or manually endorse the originality of every piece of educational material uploaded to our servers.
                        </p>
                        <p className="mb-4">
                            <strong>Coincidental Resemblance:</strong> In the academic domain, specifically concerning competitive examinations, government job preparation, and standardized tests, syllabi and objective facts are universal. Consequently, certain questions, explanations, methodologies, or study notes provided on Pariksha365 may bear a resemblance to content published by other educational technology platforms, coaching institutes, or publishing houses (including but not limited to competitors in the market).
                        </p>
                        <p className="mb-4">
                            <strong>No Intent of Plagiarism:</strong> Any such resemblance, overlap, or duplicate phrasing in fundamental academic facts, test questions, or learning structures is purely coincidental and incidental to the universal nature of the subject matter. Pariksha365 completely denies any intentional plagiarism, copyright infringement, or intellectual property violation.
                        </p>
                        <p>
                            <strong>Notice and Takedown Policy (DMCA / Copyright claims):</strong> If you believe any content on Pariksha365 infringes upon your copyright, you must submit a formal, verifiable takedown notice detailing the specific URI/URL of the allegedly infringing material and proof of original ownership. Upon receipt of a valid notice, our sole obligation and liability is limited to promptly removing or disabling access to the disputed content without admitting any liability.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">6. Limitation of Liability</h2>
                        <b className="block mb-2 font-bold uppercase text-gray-900">Maximum Extent Permitted by Law</b>
                        <p className="mb-4 text-gray-600 font-medium">
                            TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL PARIKSHA365, ITS DIRECTORS, EMPLOYEES, PARTNERS, OR AGENTS, BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES, RESULTING FROM (I) YOUR ACCESS TO OR USE OF OR INABILITY TO ACCESS OR USE THE SERVICE; (II) ANY CONDUCT OR CONTENT OF ANY THIRD PARTY ON THE SERVICE; (III) ANY CONTENT OBTAINED FROM THE SERVICE, INCLUDING CLAIMS OF PLAGIARISM OR INTELLECTUAL PROPERTY INFRINGEMENT INITIATED BY THIRD PARTIES.
                        </p>
                        <p>
                            Our platform is provided on an "AS IS" and "AS AVAILABLE" basis without warranties of any kind, whether express or implied, including, but not limited to, implied warranties of merchantability, fitness for a particular purpose, non-infringement, or course of performance.
                        </p>
                    </section>

                    <section className="bg-gray-100 p-6 rounded-lg mt-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-2">6. Indemnification</h2>
                        <p>
                            You agree to defend, indemnify and hold harmless Pariksha365 and its licensee and licensors, and their employees, contractors, agents, officers and directors, from and against any and all claims, damages, obligations, losses, liabilities, costs or debt, and expenses (including but not limited to attorney's fees), resulting from or arising out of a) your use and access of the Service, by you or any person using your account and password, or b) a breach of these Terms.
                        </p>
                    </section>

                    <section className="text-center pt-8 border-t mt-12 text-gray-500">
                        <p>If you have questions regarding this policy or wish to issue a legal notice, contact our Grievance Officer.</p>
                        <p className="mt-2 font-semibold">Pariksha365 Legal Department</p>
                    </section>
                </div>
            </div>
        </div>
    );
};
