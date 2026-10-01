(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.35cad2eeb567f632.js","sha256":"35cad2eeb567f632a895b64264f7347f266ace4db8a63a589035769609a3c9bc","count":2220,"publishedAt":"2026-10-01T07:42:57Z","state":"calendar-state.json","stateSha256":"bbeac9becde1903a5f0cbdeb05055c0c31d38258b6b334cefb1bca5f6bcb0401","sourceState":"calendar-source-state.json","sourceStateSha256":"979b015b53180dcc5f3dab3376602033437cc837365f0c98483866172c5fd76c"});
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
