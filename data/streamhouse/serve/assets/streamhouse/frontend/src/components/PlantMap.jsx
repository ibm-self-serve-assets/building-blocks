import React,{useEffect,useRef,useState} from 'react';
import {MapPin,ExternalLink} from 'lucide-react';
const bounds={lonMin:-125,lonMax:-66,latMin:24,latMax:50};
const coords=(lat,lng)=>({x:64+(lng-bounds.lonMin)/(bounds.lonMax-bounds.lonMin)*836,y:55+(bounds.latMax-lat)/(bounds.latMax-bounds.latMin)*395});
export default function PlantMap({sites,selected,onSelect}){
 const mapRef=useRef(null);const gmRef=useRef(null);const markersRef=useRef([]);const [mapError,setMapError]=useState('');
 const apiKey=import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
 useEffect(()=>{
    if(!apiKey||!mapRef.current)return;
    let cancelled=false;const init=()=>{
      if(cancelled||!mapRef.current||!window.google?.maps)return;
      gmRef.current=new window.google.maps.Map(mapRef.current,{center:{lat:38.1,lng:-97.4},zoom:4,mapId:import.meta.env.VITE_GOOGLE_MAPS_MAP_ID||undefined,styles:[{elementType:'geometry',stylers:[{color:'#12283a'}]},{elementType:'labels.text.fill',stylers:[{color:'#7b9bb0'}]},{elementType:'labels.text.stroke',stylers:[{color:'#101e2e'}]},{featureType:'water',elementType:'geometry',stylers:[{color:'#071727'}]},{featureType:'road',stylers:[{visibility:'off'}]},{featureType:'poi',stylers:[{visibility:'off'}]}],streetViewControl:false,fullscreenControl:false,mapTypeControl:false});
    };
    if(window.google?.maps){init();return()=>{cancelled=true;};}
    const callback='__factoryPulseMapsReady';window[callback]=init;
    window.gm_authFailure=()=>setMapError('Google Maps rejected the API key. Enable Maps JavaScript API + billing and allow http://localhost:5173/* as a referrer.');
    if(!document.getElementById('google-maps-js')){
      const script=document.createElement('script');script.id='google-maps-js';script.src=`https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=${callback}`;script.async=true;script.onerror=()=>setMapError('Google Maps failed to load. Check the API key and allowed referrers.');document.head.appendChild(script);
    }
    return()=>{cancelled=true;delete window[callback];};
 },[apiKey]);
 useEffect(()=>{
    if(!gmRef.current||!window.google?.maps)return;
    markersRef.current.forEach(m=>m.setMap(null));markersRef.current=[];
    for(const site of sites){
      const color=site.status==='warning'?'#ff746a':site.status==='idle'?'#a8a8a8':'#20d9bb';
      const marker=new window.google.maps.Marker({map:gmRef.current,position:{lat:site.lat,lng:site.lng},title:site.name,icon:{path:window.google.maps.SymbolPath.CIRCLE,fillColor:color,fillOpacity:1,strokeColor:'#082134',strokeWeight:3,scale:site.id===selected?12:9}});
      marker.addListener('click',()=>onSelect(site.id));markersRef.current.push(marker);
    }
 },[sites,selected,onSelect]);
 return <div className="map-area">
    {apiKey&&!mapError?<div ref={mapRef} className="google-map" aria-label="Google Maps map of six fictional US factories"/>:<div className="us-map-fallback">
      <svg viewBox="0 0 960 510" className="us-map-svg" role="img" aria-label="Illustrative contiguous United States map with six selectable factory markers">
       <defs><pattern id="mapGrid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" fill="none" stroke="#284153" strokeWidth=".8" opacity=".35"/></pattern><linearGradient id="land" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#193a4a"/><stop offset="1" stopColor="#173244"/></linearGradient></defs>
       <rect width="960" height="510" fill="#0b2030"/><rect width="960" height="510" fill="url(#mapGrid)"/>
       <path d="M74 90 L120 106 151 114 184 117 221 130 245 127 275 132 301 143 334 133 356 135 380 128 410 130 431 135 447 139 482 129 507 138 544 135 566 131 589 127 608 111 642 117 670 104 702 109 727 89 757 101 769 90 795 104 811 95 837 112 855 102 862 126 887 128 888 159 871 163 855 196 833 206 810 203 808 220 793 233 778 252 747 257 736 279 716 280 712 298 698 310 692 329 684 337 674 352 665 356 644 351 624 337 610 335 598 334 586 327 573 322 555 326 548 348 536 345 527 340 515 328 497 327 471 336 446 332 420 347 407 369 387 377 374 381 360 370 344 352 335 346 328 333 306 330 282 319 270 332 254 351 244 370 233 386 223 405 209 399 195 367 187 329 181 309 170 300 153 290 140 281 131 270 115 259 117 231 101 214 92 180 81 144 Z" fill="url(#land)" stroke="#3d6a7c" strokeWidth="2.2"/>
       <path d="M170 302L230 308 295 312 370 316 455 316 536 317M215 134L225 225 234 322M340 143L349 243 350 355M455 141L461 227 469 329M585 131L581 224 598 330M713 120L702 200 689 307" fill="none" stroke="#4a7283" strokeWidth="1" opacity=".36" strokeDasharray="3 7"/>
       {sites.map(site=>{const p=coords(site.lat,site.lng);const chosen=site.id===selected;const color=site.status==='warning'?'#ff867a':site.status==='idle'?'#9aabbc':'#24d7b4';return <g key={site.id} className="map-plant-marker" onClick={()=>onSelect(site.id)} role="button" tabIndex={0} onKeyDown={e=>{if(e.key==='Enter')onSelect(site.id)}} aria-label={`Select ${site.name}`}>
         {chosen&&<circle cx={p.x} cy={p.y} r="26" fill={color} opacity=".13"><animate attributeName="r" values="20;32;20" dur="2.4s" repeatCount="indefinite"/></circle>}
         <circle cx={p.x} cy={p.y} r={chosen?13:9.5} fill="#0c2636" stroke={color} strokeWidth="3.2"/><circle cx={p.x} cy={p.y} r="4.7" fill={color}/>
         <text x={p.x+15} y={p.y-12} fill={chosen?'white':'#b7cfdb'} fontSize={chosen?17:14} fontFamily="IBM Plex Sans,Arial" fontWeight={chosen?700:500}>{site.id}</text>
       </g>})}
       <text x="31" y="474" fill="#5e899e" fontSize="12" letterSpacing="3">NORTH AMERICA  /  OPERATIONS GRID</text><text x="932" y="474" textAnchor="end" fill="#608a9d" fontSize="12">ILLUSTRATIVE · NOT GOOGLE MAPS</text>
      </svg>
     </div>}
     <div className="map-key"><span><i className="key-dot healthy"/> Operational</span><span><i className="key-dot warning"/> Attention</span><span><i className="key-dot idle"/> Paused</span></div>
     {mapError&&<div className="map-error">{mapError}</div>}
     {apiKey&&<div className="map-service-tag">GOOGLE MAPS PLATFORM</div>}
    </div>
}
