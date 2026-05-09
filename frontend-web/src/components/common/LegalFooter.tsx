import { Link } from 'react-router-dom';

export const LegalFooter = () => (
    <footer className="w-full border-t border-gray-100 bg-white mt-auto">
        <div className="max-w-5xl mx-auto px-4 py-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-400">
            <div className="text-center sm:text-left">
                <span className="font-semibold text-gray-500">Pariksha365</span>
                <span className="mx-2">·</span>
                <span>Owned &amp; operated by <span className="font-semibold text-gray-500">LINGUTLA RAMADEVI</span></span>
            </div>
            <div className="flex items-center gap-4">
                <Link to="/privacy" className="hover:text-gray-600 transition-colors">Privacy Policy</Link>
                <Link to="/terms" className="hover:text-gray-600 transition-colors">Terms &amp; Conditions</Link>
                <a href="mailto:contact@gsicorp.in" className="hover:text-gray-600 transition-colors">Contact</a>
            </div>
        </div>
        <div className="text-center text-[11px] text-gray-300 pb-4">
            Payments secured by Cashfree · 7-day refund policy · All prices in INR
        </div>
    </footer>
);
