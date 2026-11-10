(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b99bbb3bb616a0aa.js","sha256":"b99bbb3bb616a0aabe96b0369a033c0e913d3816215da4af57b0abe427e277b3","count":180});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
