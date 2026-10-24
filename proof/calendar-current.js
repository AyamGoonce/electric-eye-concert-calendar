(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cdd1d77f202577f9.js","sha256":"cdd1d77f202577f90514ad226e27e0f9efe2de79241029037532ac1300159852","count":2079,"publishedAt":"2026-10-24T04:46:59Z","state":"calendar-state.json","stateSha256":"987b13890328c26f4fb21a33e2cdc3d1dda5b16014601422b176b4509f5ee6fd","sourceState":"calendar-source-state.json","sourceStateSha256":"c976ad0f62cc2f4392c3c29d968bac6850b924f928dc9435a64372908dd2605a"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
