(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d3777ba082886103.js","sha256":"d3777ba082886103ab6dd64ea0021cb6ab55c2634f58e6803f16b3e87b760d4c","count":1981,"publishedAt":"2026-11-08T00:45:05Z","state":"calendar-state.json","stateSha256":"5a19cf53e07c51a48335e42127ebe4fad0c35c2f77647c3e4cba2dc02ee4e17e","sourceState":"calendar-source-state.json","sourceStateSha256":"aae37b0770914ca7eb9433044226ac586f2bd82a245670cf0a2ba3b17b41110b"});
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
