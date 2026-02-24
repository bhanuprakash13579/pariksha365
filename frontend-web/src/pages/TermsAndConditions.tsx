import React from 'react';

export const TermsAndConditions: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl w-full bg-white shadow-2xl rounded-2xl p-8 sm:p-12 space-y-8 text-gray-800">
                <div className="text-center border-b pb-6 mb-8">
                    <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Terms and Conditions</h1>
                    <p className="mt-4 text-sm text-gray-500 font-medium uppercase tracking-wider">Effective Date: {new Date().toLocaleDateString()}</p>
                </div>

                <div className="space-y-8 text-sm leading-relaxed">

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">1. Acceptance of Terms</h2>
                        <p>
                            These Terms and Conditions ("Terms") constitute a legally binding agreement made between you, whether personally or on behalf of an entity ("you") and Pariksha365 ("Company", "we", "us", or "our"), concerning your access to and use of the Pariksha365 website, mobile application, and any related services (collectively, the "Site"). By accessing the Site, you agree that you have read, understood, and agreed to be bound by all of these Terms. IF YOU DO NOT AGREE WITH ALL OF THESE TERMS, THEN YOU ARE EXPRESSLY PROHIBITED FROM USING THE SITE AND MUST DISCONTINUE USE IMMEDIATELY.
                        </p>
                    </section>

                    <section className="bg-red-50 p-6 rounded-lg border border-red-100">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">2. Intermediary Status & Content Disclaimer</h2>
                        <p className="mb-4">
                            <strong>Platform Role:</strong> Pariksha365 operates as an "Intermediary" under applicable internet and information technology laws. Our platform aggregates educational content, mock tests, and study materials ("Content") provided by independent educators and third-party creators. We do not pre-screen or manually verify the originality of all Content hosted on our servers.
                        </p>
                        <p className="mb-4 font-bold text-red-800">
                            <strong>Exclusion of Liability for Intellectual Property:</strong> Because academic facts, historical data, and competitive exam syllabi are public domain and universal, Content on Pariksha365 may inadvertently resemble materials from other ed-tech platforms, coaching institutes, or publishers. Pariksha365 explicitly denies any intentional plagiarism. We claim Safe Harbor protection from direct infringement claims. Any resemblance is coincidental and structural to the nature of academic preparation.
                        </p>
                        <p>
                            <strong>DMCA/Takedown Procedure:</strong> If you represent a third-party copyright holder and believe Content on our Site infringes your rights, you must formally notify our Grievance Officer with sufficient proof. Pariksha365’s sole obligation is the prompt takedown of the disputed specific URI/URL, without any admission of fault, liability, or damages.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">3. User Representations & Conduct</h2>
                        <p className="mb-3">By using the Site, you represent and warrant that:</p>
                        <ul className="list-disc pl-5 mt-2 space-y-2 text-gray-700">
                            <li>All registration information you submit will be true, accurate, current, and complete.</li>
                            <li>You will maintain the accuracy of such information and promptly update it as necessary.</li>
                            <li>You have the legal capacity to agree to these Terms.</li>
                            <li>You will not access the Site through automated or non-human means, whether through a bot, script, or otherwise.</li>
                            <li>You will not use the Site for any illegal or unauthorized purpose.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">4. Prohibited Activities</h2>
                        <p className="mb-3">You may not access or use the Site for any purpose other than that for which we make the Site available. The Site may not be used in connection with any commercial endeavors except those that are specifically endorsed or approved by us.</p>
                        <p className="text-gray-700">As a user of the Site, you agree not to: (1) systematically retrieve data or other content from the Site to create or compile a collection, compilation, database, or directory without written permission from us; (2) trick, defraud, or mislead us and other users; (3) circumvent, disable, or otherwise interfere with security-related features of the Site; (4) disparage, tarnish, or otherwise harm, in our opinion, us and/or the Site.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">5. Limitation of Liability</h2>
                        <p className="font-bold uppercase text-gray-900 mb-2">Maximum Extent Permitted by Law</p>
                        <p className="text-gray-600 font-medium">
                            IN NO EVENT WILL WE OR OUR DIRECTORS, EMPLOYEES, OR AGENTS BE LIABLE TO YOU OR ANY THIRD PARTY FOR ANY DIRECT, INDIRECT, CONSEQUENTIAL, EXEMPLARY, INCIDENTAL, SPECIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFIT, LOST REVENUE, LOSS OF DATA, OR OTHER DAMAGES ARISING FROM YOUR USE OF THE SITE, EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, REGARDLESS OF THE LEGAL THEORY ASSERTED.
                        </p>
                    </section>

                    <section className="bg-gray-100 p-6 rounded-lg">
                        <h2 className="text-xl font-bold text-gray-900 mb-2">6. Indemnification</h2>
                        <p>
                            You agree to defend, indemnify, and hold us harmless, including our subsidiaries, affiliates, and all of our respective officers, agents, partners, and employees, from and against any loss, damage, liability, claim, or demand, including reasonable attorneys’ fees and expenses, made by any third party due to or arising out of: (1) your use of the Site; (2) breach of these Terms; (3) any breach of your representations and warranties set forth in these Terms.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">7. Modifications and Interruptions</h2>
                        <p>
                            We reserve the right to change, modify, or remove the contents of the Site at any time or for any reason at our sole discretion without notice. We will not be liable to you or any third party for any modification, price change, suspension, or discontinuance of the Site.
                        </p>
                    </section>

                    <section className="text-center pt-8 border-t mt-12 text-gray-500">
                        <p>If you have questions regarding these terms, please contact our Legal Department.</p>
                    </section>
                </div>
            </div>
        </div>
    );
};
