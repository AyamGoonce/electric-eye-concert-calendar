(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa9d72203ec820d0.js","sha256":"fa9d72203ec820d09001bc926420e083209161d9c7e663b923eb963bc4d28b50","count":2103,"publishedAt":"2026-11-16T13:35:24Z","state":"calendar-state.json","stateSha256":"3f019b41ab3d33b276b5241901eea311f672cb8277bf8f97070fa43be3e597eb","sourceState":"calendar-source-state.json","sourceStateSha256":"a28574bc50905cdbaf2b8f365b862ed66d5290ba48c73272b1ce4ee825ddf77c"});
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
