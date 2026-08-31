(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4e702bb1ab81d85e.js","sha256":"4e702bb1ab81d85e0996fecbcfe79b5f89b2a1c2fc828a5ab935978a70c460a2","count":2082,"publishedAt":"2026-08-31T14:04:04Z","state":"calendar-state.json","stateSha256":"2b55672553e2178598a6115265f2b9604b629b372216e2298a9c9bcfa2a6cb91"});
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
