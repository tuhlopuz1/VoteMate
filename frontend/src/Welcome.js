import { useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { 
  FiUserCheck, 
  FiBarChart2, 
  FiZap, 
  FiShield, 
  FiSend, 
  FiSliders 
} from "react-icons/fi";
import FeatureCard from "./components/FeatureCard.js";
import './styles/welcome.css';
import Navbar from "./components/NavBar";
import Footer from "./components/Footer";

const WelcomePage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      navigate('/home');
    }
  }, [navigate]);

  const features = [
    {
      icon: <FiUserCheck className="icon" />,
      title: "Private & Anonymous",
      description: "All votes are fully anonymous. No tracking, no identities stored — your privacy is guaranteed."
    },
    {
      icon: <FiBarChart2 className="icon" />,
      title: "Transparent Results",
      description: "Real-time and tamper-proof results you can trust. Built with transparency in mind."
    },
    {
      icon: <FiZap className="icon" />,
      title: "Instant Demo Mode",
      description: "Try the platform without creating an account. Great for quick decisions and testing features."
    },
    {
      icon: <FiShield className="icon" />,
      title: "Fraud Prevention",
      description: "Vote integrity is our priority — we prevent spam, duplicates, and manipulation automatically."
    },
    {
      icon: <FiSend className="icon" />,
      title: "Simple Participation",
      description: "Easy to join and vote — just share a link. No confusing setup or login required."
    },
    {
      icon: <FiSliders className="icon" />,
      title: "Flexible Poll Options",
      description: "Single or multiple choice, deadlines, access control — you set the rules."
    }
  ];

  return (
    <div className="welcome-page">
      <Navbar/>
      <div className="container">
        {/* Hero Section */}
        <div className="hero-section">
          <h1 className="hero-title">
            Welcome to <span className="app-name">VoteMate</span>
          </h1>
          <p className="hero-description">
            A secure, anonymous voting platform for teams, communities, and events. Make your voice heard — privately and effortlessly.
          </p>
          <div className="cta-buttons">
            <Link to="/signup" className="cta-button primary">Get Started</Link>
            <Link to="/login" className="cta-button secondary">Log in</Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="features-section">
          <div className="features-grid">
            {features.map((feature, index) => (
              <FeatureCard 
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default WelcomePage;
