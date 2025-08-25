import React, { useState, createContext, useContext, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useToast } from '../hooks/use-toast';
import { Wallet, LogIn, UserPlus, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';

// Create authentication context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: null,
      login: () => {},
      logout: () => {},
      register: () => {},
      isAuthenticated: false,
      loading: false
    };
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Check for existing session on app start
  useEffect(() => {
    const savedUser = localStorage.getItem('casino_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('casino_user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (walletAddress, password) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
        wallet_address: walletAddress,
        password: password
      });

      if (response.data.success) {
        const userData = {
          wallet_address: walletAddress,
          user_id: response.data.user_id,
          created_at: response.data.created_at
        };
        setUser(userData);
        localStorage.setItem('casino_user', JSON.stringify(userData));
        return { success: true };
      } else {
        return { success: false, error: response.data.message };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const register = async (walletAddress, password) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/register`, {
        wallet_address: walletAddress,
        password: password
      });

      if (response.data.success) {
        const userData = {
          wallet_address: walletAddress,
          user_id: response.data.user_id,
          created_at: response.data.created_at
        };
        setUser(userData);
        localStorage.setItem('casino_user', JSON.stringify(userData));
        return { success: true };
      } else {
        return { success: false, error: response.data.message };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('casino_user');
  };

  return (
    <AuthContext.Provider 
      value={{
        user,
        login,
        logout,
        register,
        isAuthenticated: !!user,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

const LoginForm = ({ onClose }) => {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [loginType, setLoginType] = useState('username'); // 'username' or 'wallet'
  const [username, setUsername] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login, register, setUser } = useAuth();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (mode === 'login') {
      // Login mode
      if (loginType === 'username') {
        if (!username || !password) {
          toast({
            title: "Missing Information",
            description: "Please provide both username and password",
          });
          return;
        }
      } else {
        if (!walletAddress || !password) {
          toast({
            title: "Missing Information", 
            description: "Please provide both wallet address and password",
          });
          return;
        }
      }
    } else {
      // Register mode
      if (!walletAddress || !password) {
        toast({
          title: "Missing Information",
          description: "Please provide both wallet address and password",
        });
        return;
      }
    }

    setLoading(true);
    
    try {
      let result;
      
      if (mode === 'login' && loginType === 'username') {
        // Username login
        result = await loginWithUsername(username, password);
      } else if (mode === 'login') {
        // Wallet address login
        result = await login(walletAddress, password);
      } else {
        // Registration
        result = await register(walletAddress, password, username);
      }

      if (result.success) {
        toast({
          title: mode === 'login' ? "Login Successful!" : "Registration Successful!",
          description: `Welcome${result.username ? `, ${result.username}` : ''}!`,
        });
        onClose();
      } else {
        toast({
          title: mode === 'login' ? "Login Failed" : "Registration Failed",
          description: result.error,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred",
      });
    } finally {
      setLoading(false);
    }
  };

  const loginWithUsername = async (username, password) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await axios.post(`${backendUrl}/api/auth/login-username`, {
        username: username,
        password: password
      });

      if (response.data.success) {
        const userData = {
          user_id: response.data.user_id,
          username: response.data.username,
          wallet_address: response.data.wallet_address,
          created_at: response.data.created_at
        };

        localStorage.setItem('casino_user', JSON.stringify(userData));
        setUser(userData); // Fix: Update React authentication state
        return { success: true, username: response.data.username };
      } else {
        return { success: false, error: response.data.message || "Invalid credentials" };
      }
    } catch (error) {
      console.error('Username login error:', error);
      return { success: false, error: "Connection failed. Please try again." };
    }
  };

  const generateSampleWallet = () => {
    // Generate a sample wallet address for demo purposes
    const sampleWallets = [
      'RealWallet9876543210XYZ',
      'CRTHolder1234567890ABC', 
      'DOGEFan5678901234DEF',
      'TRXInvestor234567GHI'
    ];
    const randomWallet = sampleWallets[Math.floor(Math.random() * sampleWallets.length)];
    setWalletAddress(randomWallet);
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/50 max-w-md w-full">
        <div className="space-y-6">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
              <Wallet className="w-8 h-8 text-black" />
            </div>
            <h2 className="text-2xl font-bold text-yellow-400 mb-2">
              {mode === 'login' ? 'Login to Casino' : 'Create Account'}
            </h2>
            <p className="text-gray-300 text-sm">
              {mode === 'login' 
                ? 'Enter your wallet address to access your account' 
                : 'Create a new account to start saving and playing'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'login' && (
              <div className="flex justify-center mb-4">
                <div className="bg-gray-800 rounded-lg p-1 flex">
                  <button
                    type="button"
                    onClick={() => setLoginType('username')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      loginType === 'username' 
                        ? 'bg-yellow-500 text-black' 
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    Username
                  </button>
                  <button
                    type="button"
                    onClick={() => setLoginType('wallet')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      loginType === 'wallet' 
                        ? 'bg-yellow-500 text-black' 
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    Wallet Address
                  </button>
                </div>
              </div>
            )}

            {mode === 'login' && loginType === 'username' ? (
              <div className="space-y-2">
                <label className="text-sm text-gray-300">Username</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="bg-black/30 border-gray-600 text-white"
                />
              </div>
            ) : (
              <div className="space-y-2">
                <label className="text-sm text-gray-300">
                  {mode === 'register' ? 'Wallet Address' : 'Wallet Address'}
                </label>
                <div className="relative">
                  <Input
                    type="text"
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                    placeholder="Enter your wallet address"
                    className="bg-black/30 border-gray-600 text-white pr-20"
                  />
                  <Button
                    type="button"
                    onClick={generateSampleWallet}
                    className="absolute right-1 top-1 h-8 px-2 text-xs bg-blue-600 hover:bg-blue-500"
                  >
                    Demo
                  </Button>
                </div>
              </div>
            )}

            {mode === 'register' && (
              <div className="space-y-2">
                <label className="text-sm text-gray-300">Username (Optional)</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Choose a username (optional)"
                  className="bg-black/30 border-gray-600 text-white"
                />
                <p className="text-xs text-gray-400">Leave blank to auto-generate from wallet address</p>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm text-gray-300">Password</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="bg-black/30 border-gray-600 text-white pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold hover:from-yellow-300 hover:to-yellow-500"
            >
              {loading ? 'Processing...' : mode === 'login' ? 'Login' : 'Create Account'}
              {mode === 'login' ? <LogIn className="w-4 h-4 ml-2" /> : <UserPlus className="w-4 h-4 ml-2" />}
            </Button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                className="text-yellow-400 hover:text-yellow-300 text-sm"
              >
                {mode === 'login' 
                  ? "Don't have an account? Register here" 
                  : "Already have an account? Login here"}
              </button>
            </div>
          </form>

          <Button
            onClick={onClose}
            variant="ghost"
            className="w-full text-gray-400 hover:text-white"
          >
            Close
          </Button>
        </div>
      </Card>
    </div>
  );
};

export const AuthModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;
  return <LoginForm onClose={onClose} />;
};

export default LoginForm;