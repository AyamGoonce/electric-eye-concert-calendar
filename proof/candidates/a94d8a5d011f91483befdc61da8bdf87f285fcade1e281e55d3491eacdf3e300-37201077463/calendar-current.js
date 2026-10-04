(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a94d8a5d011f9148.js","sha256":"a94d8a5d011f91483befdc61da8bdf87f285fcade1e281e55d3491eacdf3e300","count":2182,"publishedAt":"2026-10-04T12:10:45Z","state":"calendar-state.json","stateSha256":"e4ad34da6b4878addc9ea0423e47aec1557ba2e486024490fc92a938383449a4","sourceState":"calendar-source-state.json","sourceStateSha256":"ee9c938ef77d3cb63c862c30c383f441e0db0cb695dfef51b1680d1618c964c5"});
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
