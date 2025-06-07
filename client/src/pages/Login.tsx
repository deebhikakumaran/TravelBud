
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    try {
      await login(email, password);
      toast({
        title: "Welcome back!",
        description: "Successfully logged in",
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Error",
        description: "Invalid credentials",
        variant: "destructive",
      });
    }
  };

  const handleDemoLogin = async () => {
    try {
      await login('demo@travelai.com', 'demo123');
      toast({
        title: "Login Successful!",
        description: "Welcome to TravelBud",
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Error",
        description: "Login failed",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl font-bold text-white">
                TravelBud
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex items-center justify-center p-4 min-h-[calc(100vh-80px)]">
        <div className="w-full max-w-md">
          <Card className="bg-gray-900 border-gray-800 shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-white">Sign In</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Demo Login Button */}
              <div className="mb-6">
                <Button 
                  onClick={handleDemoLogin}
                  className="w-full mb-4 border-gray-600 bg-gray-600/10 hover:bg-gray-600/20 text-white"
                  disabled={isLoading}
                >
                  Try Demo Login
                </Button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-gray-300">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="mt-1 bg-gray-800 border-gray-700 text-white placeholder-gray-500"
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-gray-300">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="mt-1 bg-gray-800 border-gray-700 text-white placeholder-gray-500"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-gray-800 text-white hover:bg-gray-700 mt-3 p-2" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Signing In...' : 'Sign In'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 px-6 border-t border-gray-800">
        <div className="container mx-auto">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <span className="text-xl font-bold text-white">
                TravelBud
              </span>
            </div>
            <p className="text-gray-400 text-sm max-w-md mx-auto">
              Your smart travel companion
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Login;
