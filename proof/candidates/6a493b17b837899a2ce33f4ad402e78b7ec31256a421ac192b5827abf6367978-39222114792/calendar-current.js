(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6a493b17b837899a.js","sha256":"6a493b17b837899a2ce33f4ad402e78b7ec31256a421ac192b5827abf6367978","count":2055,"publishedAt":"2026-10-19T08:23:06Z","state":"calendar-state.json","stateSha256":"7cbb7b651a6df6bc4871f0aeb18bc48ffaa7a2bf7400d6e0957f39274d4d9d1a","sourceState":"calendar-source-state.json","sourceStateSha256":"78a3a2887bf697dda70b57eae318dcc9048e4dcf69e9ec1549b5e5e96807e222"});
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
