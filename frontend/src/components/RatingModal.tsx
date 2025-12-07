import { useState } from 'react';
import './RatingModal.css';

interface RatingModalProps {
    requestId: number;
    requestNumber: string;
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (rating: RatingData) => Promise<void>;
}

export interface RatingData {
    timeliness_score: number;
    quality_score: number;
    communication_score: number;
    professionalism_score: number;
    overall_score: number;
    comments?: string;
}

export const RatingModal = ({ requestNumber, isOpen, onClose, onSubmit }: RatingModalProps) => {
    const [timeliness, setTimeliness] = useState(0);
    const [quality, setQuality] = useState(0);
    const [communication, setCommunication] = useState(0);
    const [professionalism, setProfessionalism] = useState(0);
    const [comments, setComments] = useState('');
    const [submitting, setSubmitting] = useState(false);

    // Calculate overall score (average of 4 dimensions)
    const overallScore = timeliness && quality && communication && professionalism
        ? ((timeliness + quality + communication + professionalism) / 4).toFixed(1)
        : '0.0';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate all scores are set
        if (!timeliness || !quality || !communication || !professionalism) {
            alert('Please rate all dimensions');
            return;
        }

        setSubmitting(true);
        try {
            await onSubmit({
                timeliness_score: timeliness,
                quality_score: quality,
                communication_score: communication,
                professionalism_score: professionalism,
                overall_score: Math.round((timeliness + quality + communication + professionalism) / 4),
                comments: comments || undefined
            });

            // Reset form
            setTimeliness(0);
            setQuality(0);
            setCommunication(0);
            setProfessionalism(0);
            setComments('');

            onClose();
        } catch (error) {
            console.error('Failed to submit rating:', error);
            alert('Failed to submit rating. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content rating-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Rate Request {requestNumber}</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="rating-section">
                        <RatingDimension
                            label="Timeliness"
                            description="How quickly was the request fulfilled?"
                            value={timeliness}
                            onChange={setTimeliness}
                        />

                        <RatingDimension
                            label="Quality"
                            description="How well was the work done?"
                            value={quality}
                            onChange={setQuality}
                        />

                        <RatingDimension
                            label="Communication"
                            description="How well did they communicate?"
                            value={communication}
                            onChange={setCommunication}
                        />

                        <RatingDimension
                            label="Professionalism"
                            description="How professional was the interaction?"
                            value={professionalism}
                            onChange={setProfessionalism}
                        />

                        <div className="overall-score">
                            <div className="overall-label">Overall Score</div>
                            <div className="overall-value">{overallScore} / 5.0</div>
                        </div>

                        <div className="form-group">
                            <label>Comments (Optional)</label>
                            <textarea
                                value={comments}
                                onChange={(e) => setComments(e.target.value)}
                                placeholder="Share your feedback..."
                                rows={4}
                                maxLength={1000}
                            />
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={onClose} disabled={submitting}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary" disabled={submitting}>
                            {submitting ? 'Submitting...' : 'Submit Rating'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

// Star Rating Component
interface RatingDimensionProps {
    label: string;
    description: string;
    value: number;
    onChange: (value: number) => void;
}

const RatingDimension = ({ label, description, value, onChange }: RatingDimensionProps) => {
    const [hover, setHover] = useState(0);

    return (
        <div className="rating-dimension">
            <div className="dimension-header">
                <div className="dimension-label">{label}</div>
                <div className="dimension-description">{description}</div>
            </div>
            <div className="stars">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        type="button"
                        className={`star ${star <= (hover || value) ? 'filled' : ''}`}
                        onClick={() => onChange(star)}
                        onMouseEnter={() => setHover(star)}
                        onMouseLeave={() => setHover(0)}
                    >
                        ★
                    </button>
                ))}
                <span className="score-text">{value > 0 ? `${value}/5` : ''}</span>
            </div>
        </div>
    );
};
