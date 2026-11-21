(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4d76f5f0d0a5fea7.js","sha256":"4d76f5f0d0a5fea76b74489a6be86f33b45051e8840f94d08b014941be9a2dd6","count":2130,"publishedAt":"2026-11-21T19:23:39Z","state":"calendar-state.json","stateSha256":"df59a75495cf19c8c2bdcc0e2d4b518c3d5e9540a30146b050bd88cbf1c22cf1","sourceState":"calendar-source-state.json","sourceStateSha256":"7e319da669cda3e255a30862db5f46e8965917b26c1cbbfc8c7f87db4f9831f2"});
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
