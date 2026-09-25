(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4a9a1740a1883147.js","sha256":"4a9a1740a1883147bdb17f74cc8c11278ed385bbc0c975f222ed53bfa40c983a","count":2122,"publishedAt":"2026-09-25T21:42:55Z","state":"calendar-state.json","stateSha256":"dd2cb689c6d721867b78441f98d72f933605311336cc16df70d3881e1bed2741","sourceState":"calendar-source-state.json","sourceStateSha256":"d809f1cf98c7d65bb998ba33d8714a4e33457dde40bd5ae2af2524138ab31337"});
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
