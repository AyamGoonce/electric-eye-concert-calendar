(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e32601da71cd32e9.js","sha256":"e32601da71cd32e9e05957b21a53b52ad69ecd65f106df39177944be00167bb4","count":2153,"publishedAt":"2026-11-13T11:15:50Z","state":"calendar-state.json","stateSha256":"3ad1c1c1fe6b15361e796560b43d4624777bfc84d3db07013180e91abb5aa37a","sourceState":"calendar-source-state.json","sourceStateSha256":"dc4a1d29579a916fa67f7072fb10649c59b2becf4725c964c7f0202ff7f18798"});
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
