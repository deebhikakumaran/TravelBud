import { MapPin } from 'lucide-react';

interface Trip {
  id: number;
  destination: string;
  dates: string;
  budget: string;
  status: string;
  coordinates: [number, number];
}

interface MapViewProps {
  trips: Trip[];
}

const MapView = ({ trips }: MapViewProps) => {
  return (
    <div className="w-full h-full bg-gray-800 rounded-lg relative overflow-hidden">
      {/* World Map Background (simplified SVG) */}
      <div className="absolute inset-0 flex items-center justify-center">
        <svg
          viewBox="0 0 1000 500"
          className="w-full h-full opacity-40 text-white"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Simplified world map outline */}
          <path
            d="M150 200C200 150 250 140 300 160C350 180 400 170 450 190C500 210 550 200 600 220C650 240 700 230 750 250C800 270 850 260 900 280"
            stroke="white"
            strokeWidth="2"
            fill="none"
          />
          <path
            d="M100 250C150 230 200 240 250 220C300 200 350 210 400 190C450 170 500 180 550 160C600 140 650 150 700 130"
            stroke="white"
            strokeWidth="2"
            fill="none"
          />
          <path
            d="M80 300C130 280 180 290 230 270C280 250 330 260 380 240C430 220 480 230 530 210C580 190 630 200 680 180"
            stroke="white"
            strokeWidth="2"
            fill="none"
          />
        </svg>
      </div>

      {/* Trip Markers */}
      <div className="absolute inset-0">
        {/* Paris */}
        <div 
          className="absolute transform -translate-x-1/2 -translate-y-1/2"
          style={{ left: '45%', top: '35%' }}
        >
          <div className="relative group">
            <MapPin className="w-6 h-6 text-red-500 drop-shadow-lg animate-pulse" />
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-black text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                Paris, France
              </div>
            </div>
          </div>
        </div>

        {/* Tokyo */}
        <div 
          className="absolute transform -translate-x-1/2 -translate-y-1/2"
          style={{ left: '85%', top: '40%' }}
        >
          <div className="relative group">
            <MapPin className="w-6 h-6 text-blue-500 drop-shadow-lg animate-pulse" />
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-black text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                Tokyo, Japan
              </div>
            </div>
          </div>
        </div>

        {/* New York */}
        <div 
          className="absolute transform -translate-x-1/2 -translate-y-1/2"
          style={{ left: '25%', top: '45%' }}
        >
          <div className="relative group">
            <MapPin className="w-6 h-6 text-green-500 drop-shadow-lg animate-pulse" />
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-black text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                New York, USA
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Map Info */}
      <div className="absolute bottom-4 left-4 bg-black/60 rounded-lg p-3">
        <h4 className="text-white text-sm font-semibold mb-2">Travel Map</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center text-red-400">
            <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
            Upcoming
          </div>
          <div className="flex items-center text-blue-400">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
            Planning
          </div>
          <div className="flex items-center text-green-400">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Completed
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
