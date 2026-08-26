(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c6469d8a39270ea3.js","sha256":"c6469d8a39270ea30259ec6e5d4dff135675ac18de87d85808a57a7f5663e057","count":1740,"publishedAt":"2026-08-26T12:02:38Z","state":"calendar-state.json","stateSha256":"b2685704e7a90eb025533a675b6a158c415bc979f489f12ee9d930c8889dfc7e"});
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
