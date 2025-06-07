import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Plane, Shield, Zap, ArrowRight} from 'lucide-react';
import { motion } from 'framer-motion';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: MessageSquare,
      title: 'AI Travel Assistant',
      description: 'Chat with our intelligent assistant to plan your perfect trip',
      color: 'bg-gray-800 text-blue-400'
    },
    {
      icon: Plane,
      title: 'Smart Booking',
      description: 'Discover the best flights, hotels, and activities through our agent network',
      color: 'bg-gray-800 text-purple-400'
    },
    {
      icon: Shield,
      title: 'Budget Monitoring',
      description: 'Real-time cost tracking with smart suggestions to stay within budget',
      color: 'bg-gray-800 text-green-400'
    },
    {
      icon: Zap,
      title: 'Smart Alerts',
      description: 'Get notified about better deals and budget-friendly alternatives',
      color: 'bg-gray-800 text-orange-400'
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div>
                <span className="text-2xl font-bold text-white">
                  TravelBud
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button onClick={() => navigate('/login')} className="bg-white text-black hover:bg-gray-200">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/badcfe62-00a9-427b-9a82-ae50837a11c8.png" 
            alt="Travel inspiration" 
            className="w-full h-full object-cover opacity-40"
          />
          <div className="absolute inset-0 bg-black bg-opacity-50"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 container mx-auto px-6 py-20">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center px-6 py-3 bg-gray-800/80 backdrop-blur-sm rounded-full text-white text-sm font-medium mb-8"
            >
              <Zap className="w-4 h-4 mr-2" />
              Powered by FetchAI
            </motion.div>

            {/* Main Heading */}
            <motion.h1 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-3xl md:text-4xl lg:text-4xl font-bold text-white mb-8 leading-tight"
            >
              TravelBud
            </motion.h1>

            {/* Subtitle */}
            <motion.p 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-base md:text-lg text-gray-200 mb-12 leading-relaxed max-w-3xl mx-auto"
            >
              We lead the way in advancing intelligent travel planning through AI agent networks, 
              creating personalized experiences that adapt to your needs.
            </motion.p>

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <Button 
                size="sm" 
                className="bg-white text-black hover:bg-gray-200 text-base px-8 py-4 h-auto font-semibold shadow-2xl"
                onClick={() => navigate('/login')}
              >
                Start Planning Now
                <ArrowRight className="ml-3 w-6 h-6" />
              </Button>
            </motion.div>

          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-black">
        <div className="container mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Areas of Innovation
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Our platform connects multiple specialized agents to revolutionize your planning
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -10 }}
              >
                <Card className="border border-gray-800 shadow-lg hover:shadow-2xl transition-all duration-500 bg-gray-900 backdrop-blur-sm group h-full">
                  <CardHeader className="text-center pb-4">
                    <div className={`w-16 h-16 ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className="w-8 h-8" />
                    </div>
                    <CardTitle className="text-xl font-bold text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-center text-gray-300 leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

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

export default Landing;
