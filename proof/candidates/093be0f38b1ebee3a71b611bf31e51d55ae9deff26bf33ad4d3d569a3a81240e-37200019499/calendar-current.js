(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.093be0f38b1ebee3.js","sha256":"093be0f38b1ebee3a71b611bf31e51d55ae9deff26bf33ad4d3d569a3a81240e","count":2182,"publishedAt":"2026-10-04T11:51:57Z","state":"calendar-state.json","stateSha256":"06d49492975ce325a5579fef8be99cba144cba889dfbbb399f5264c0beb0650a","sourceState":"calendar-source-state.json","sourceStateSha256":"4e30096248ade2822671752d39b18d704f092f606cf0c5352036cf0c933e98c1"});
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
