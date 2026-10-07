(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8419625d67054313.js","sha256":"8419625d670543134ffdfc560ad41ed102d2369aaf6ee29f552250296722106d","count":2209,"publishedAt":"2026-10-07T12:12:30Z","state":"calendar-state.json","stateSha256":"14b88cab6216ea46f8f6c5286bddfca53a337b28384e8f495e49956edb8c16a3","sourceState":"calendar-source-state.json","sourceStateSha256":"4b04231ccd0231c3fdd20e0f08282920287036daad853118e3584dcabfa67573"});
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
