import { Link } from "react-router-dom";
import Logo from "./Logo";
import "../styles/navbar.css";

const Navbar = ({ currentPath }) => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-inner">
          <Link to="/">

              <Logo />

          </Link>


          <div className="navbar-actions">
            <Link to="/login" className="button login-btn">

                Log in

            </Link>
            <Link to="/signup" className="button signup-btn">

                Sign up

            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
