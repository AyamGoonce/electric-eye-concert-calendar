(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ea80e55e80471a72.js","sha256":"ea80e55e80471a7225e7115e7e7d8abbc71c55b5138c8010ae50065242eb0534","count":2472,"publishedAt":"2026-09-07T12:50:54Z","state":"calendar-state.json","stateSha256":"3542dbe41f961189687dfbeccfbed983ceac48a315c04f87cfda6f58e10019b7"});
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
