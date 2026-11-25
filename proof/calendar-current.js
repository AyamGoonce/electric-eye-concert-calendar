(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8248d984a5748463.js","sha256":"8248d984a5748463d1c52a0505e5330da4a4dd5ed80e4196fc4c71d6477c3583","count":2128,"publishedAt":"2026-11-25T19:22:40Z","state":"calendar-state.json","stateSha256":"8900ae4ea5ede5c077153ad523f47d8dda3255fc810857558c75b57180b38def","sourceState":"calendar-source-state.json","sourceStateSha256":"79d142f3720ff2fb7858a4368a043af64530833ef6f5ee01243335e3aea343f9"});
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
