import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { getApiUrl } from '../services/api';

interface PDFViewerModalProps {
    requestId: number;
    requestNumber: string;
    isOpen: boolean;
    onClose: () => void;
}

export const PDFViewerModal = ({ requestId, requestNumber, isOpen, onClose }: PDFViewerModalProps) => {
    const { token } = useAuth();
    const [loading, setLoading] = useState(false);
    const [pdfUrl, setPdfUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let objectUrl: string | null = null;

        const loadPdf = async () => {
            if (!isOpen || !token) return;
            setLoading(true);
            setError(null);
            try {
                const apiBase = getApiUrl();
                const response = await fetch(`${apiBase}/api/requests/${requestId}/pdf`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(text || 'Failed to generate PDF');
                }

                const blob = await response.blob();
                objectUrl = URL.createObjectURL(blob);
                setPdfUrl(objectUrl);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load PDF');
            } finally {
                setLoading(false);
            }
        };

        loadPdf();

        return () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
            setPdfUrl(null);
            setError(null);
        };
    }, [isOpen, requestId, token]);

    if (!isOpen) return null;

    const handleDownload = () => {
        if (!pdfUrl) return;
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `Request_${requestNumber}.pdf`;
        link.click();
    };

    return (
        <div
            className="modal-overlay"
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '20px'
            }}
            onClick={onClose}
        >
            <div
                className="modal-content"
                style={{
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    width: '90%',
                    maxWidth: '1200px',
                    height: '90vh',
                    display: 'flex',
                    flexDirection: 'column',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '20px 24px',
                        borderBottom: '1px solid #e0e0e0',
                        backgroundColor: '#f8f9fa'
                    }}
                >
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#610100' }}>
                            Request PDF - {requestNumber}
                        </h2>
                        <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '0.9rem' }}>
                            Preview and download request document
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <button
                            onClick={handleDownload}
                            className="btn btn-primary"
                            style={{ minWidth: '120px' }}
                        >
                            Download
                        </button>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                padding: '8px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'background 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                        >
                            <X size={24} color="#610100" />
                        </button>
                    </div>
                </div>

                {/* PDF Viewer */}
                <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                    {loading && (
                        <div style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            zIndex: 10
                        }}>
                            <div className="spinner"></div>
                            <p style={{ textAlign: 'center', marginTop: '16px', color: '#666' }}>
                                Generating PDF...
                            </p>
                        </div>
                    )}
                    {error && !loading && (
                        <div style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            color: '#b71c1c',
                            textAlign: 'center'
                        }}>
                            <p style={{ marginBottom: '0.5rem' }}>Unable to load PDF</p>
                            <code style={{ fontSize: '0.85rem' }}>{error}</code>
                        </div>
                    )}
                    {pdfUrl && !loading && !error && (
                        <iframe
                            src={pdfUrl}
                            style={{
                                width: '100%',
                                height: '100%',
                                border: 'none'
                            }}
                            title={`PDF Preview - ${requestNumber}`}
                        />
                    )}
                </div>

                {/* Footer */}
                <div
                    style={{
                        padding: '16px 24px',
                        borderTop: '1px solid #e0e0e0',
                        backgroundColor: '#f8f9fa',
                        display: 'flex',
                        justifyContent: 'flex-end',
                        gap: '12px'
                    }}
                >
                    <button
                        onClick={onClose}
                        className="btn btn-secondary"
                        style={{ minWidth: '100px' }}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};
